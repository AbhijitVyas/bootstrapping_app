from scripts import cores
from nltk.stem.porter import *

stemmer = PorterStemmer()

# Entity Dimensions
colors = ['white','black','grey','violet','blue','brown','green','orange','pink','purple','red','yellow','blond','olive','pastel','salmon']
sizes = ['small','little','tiny','mini','big','large','huge','tall','short','smaller','bigger','larger','taller','shorter','wide','narrow','long']
consistencies = ['amorphous','viscous','hard','gas','porosity','soft','solid','thick','thin','brittle','liquid']
shapes = ['circular','square','triangular','box','spiral','curved','convex','concave','rounded','round']
material = ['plastic','glass','rubber','opaque','transparent']
# Entity Forms and Types
viscous = ['honey','batter','syrup','sauce','ketchup','paste','glycerin','melted chocolate','corn syrup','tomato paste','chocolate','molasses','jam','maple syrup','pancake batter']
nviscous = ['water','milk','juice','alcohol','oil','vinegar','broth','wine','stock','soy sauce','soup']
powdered = ['salt','sugar','pepper','flour','tumeric powder','garlic powder','starch','cinnamon','paprika','cheese','cocoa']
# Verbs and Adverbs
slow_pouring = ['trickle','drip','dribble','drizzle','ooze','percolate','seep','distil','sprinkle','squeeze']
fast_pouring = ['pour','gush','stream','spill','jet','well' 'out','flood','sloosh','surge','emanate','discharge','pour out','cascade','tumble','spurt','shoot','expel']
adverbs = ['slowly','gently','cautiously','steadily','gradually','carefully','deliberately','moderately','tardily']
shakes = ['shake','joggle','waggle','jerk','vibrate','shudder','rattle','quiver','tumble','sprinkle','agitate']
fires = ['fire','flame','burns','flames']
plants = ['plant','fruit','vegetable','flower','tree','sapling']
# Pickups
picks = ['pick','lift','hold','grab','grasp','take']
def prop_finder(v):
    props ={}
    if not isinstance(v,list):
        v = list(v)
    if v:
        for pr in v:
            # ToDo Use stemmer/lemmatizer for each word
            if pr in colors:
                props['color'] = pr
            elif pr in sizes:
                props['size'] = pr
            elif pr in consistencies:
                props['consistency'] = pr
            elif pr in shapes:
                props['shape'] = pr
            elif pr in material:
                props['material'] = pr
    return props
def action_verb_finder(intent,dix):
    found_common = ""
    act_verb = ""

    if intent == "pouring":
        if 'ADV' in dix:
            advs = list(dix['ADV'].keys())
            found_common = bool(set(advs) & set(adverbs))
            # print(found_common)
            # if found_common:
            #     print("SLOW POURING")
            # else:
            #     print("FAST POURING")

        if 'VERB' in dix:
            vbs = list(dix['VERB'].keys())
            for vs in vbs:
                if vs in slow_pouring:
                    act_verb = vs
                elif vs in fast_pouring:
                    act_verb = vs
                elif found_common:
                    act_verb = 'drizzle'
                else:
                    act_verb = 'pour'

    elif intent == "shake":
        if 'VERB' in dix:
            vbs = list(dix['VERB'].keys())
            for vs in vbs:
                if vs in shakes:
                    act_verb = vs
                else:
                    act_verb = "shake"

    return act_verb
def motion_finder(intent=None,source=None,destination=None,stuff=None,action_verb=None,dix=None):
    motion = ""
    goal = ""
    if intent == "pouring":
        motion = 'tilt'
        if action_verb == "squeeze":
            motion = 'squeeze'
        elif stemmer.stem(stuff) in powdered:
            motion = 'shake'
            if not destination is None:
                if stemmer.stem(destination) in fires: motion = 'throw'
                if stemmer.stem(destination) in plants: motion = 'sprinkle'
        else:
            if not destination is None:
                if stemmer.stem(destination) in fires: motion = 'throw'
                if stemmer.stem(destination) in plants: motion = 'sprinkle'


    elif intent == "shake":
        motion = "shake"
        # goal = "no spillage"

    elif intent == "pick_up":
        motion = "lift"

    elif intent == "drop":
        motion = "drop"

    return motion,goal
def postprocess(rasa_out, compound_props):

    intent = ""
    ins1 = None
    act = ""
    goal = ""

    for k, v in rasa_out.items():
        if k == "intent":
            intent = v["name"]
        elif k == "entities":
            if intent == "pouring":
                ins1 = cores.Pouring()
                # Extracting RASA outputs source,destination,stuff
                try:
                    for dic in v:
                        if dic['extractor'] == "DIETClassifier" and dic['entity'] == "location" and dic['role'] == "source":
                            ins1.source = dic['value']
                        elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "location" and \
                                dic['role'] == "destination":
                            ins1.destination = dic['value']
                        elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "stuff":
                            ins1.stuff = dic['value']
                        elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and \
                                dic['role'] == "quantity":
                            ins1.amount = dic['value']
                        elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and dic[
                            'role'] == "units":
                            ins1.units = dic['value']
                        elif dic['extractor'] == "RegexEntityExtractor" and dic['entity'] == "stuff":
                            if ins1.stuff is not None:
                                ins1.stuff = dic['value']
                        elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "CARDINAL":
                            # if ins1.amount is not None:
                            ins1.amount = dic['value']
                        elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "QUANTITY":
                            # if ins1.amount is not None:
                            ins1.amount = dic['value']
                except:
                    print("Problem with Parsing RASA output")

                for key, value in compound_props['props'].items():
                    if key == ins1.source:
                        ins1.source_prop = prop_finder(value)
                    elif key == ins1.destination:
                        ins1.destination_prop = prop_finder(value)
                    elif key == ins1.stuff:
                        ins1.stuff_prop = prop_finder(value)

                for key,value in compound_props['compounds_words'].items():
                    if value == ins1.source:
                        ins1.source_prop.update({'metadata':key})
                    elif value == ins1.destination:
                        ins1.destination_prop.update({'metadata':key})
                    elif value == ins1.stuff:
                        ins1.stuff_prop.update({'metadata':key})

                # act = action_verb_finder(intent,compound_props['verbs'])
                try:
                    act, goal = testing_finder(intent=intent, source=ins1.source, destination=ins1.destination,
                                               stuff=ins1.stuff, dix=compound_props['verbs'])
                    ins1.action_verb = act
                    ins1.goal = goal
                except:
                    print("Problem with action testing finder")

                # if len(act) > 0:
                #     if ins1.stuff in viscous and act not in slow_pouring:
                #         ins1.action_verb = 'drizzle'
                #     elif ins1.stuff in powdered:
                #         ins1.action_verb = 'sprinkle'
                #     # elif ins1.stuff in nviscous and act not in slow_pouring:
                #     else:
                #         ins1.action_verb = act
                # else:
                #     print("No POS Verb")
                #     pouring_verbs = slow_pouring + fast_pouring
                #     common_verb = [word for word in compound_props['compounded_text'].split(" ") if word in pouring_verbs]
                #     ins1.action_verb = common_verb[0]

                try:
                    motion, _ = motion_finder(intent=intent, source=ins1.source, destination=ins1.destination,
                                              stuff=ins1.stuff, action_verb=ins1.action_verb,
                                              dix=compound_props['verbs'])
                    ins1.motion = motion
                except:
                    print("Problem with motion finder")



            elif intent == "shake":
                ins1 = cores.Shake()
                for dic in v:
                    if dic['extractor'] == "DIETClassifier" and dic['entity'] == "obj_to_be_shaken":
                        ins1.obj_to_be_shaken = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "location" and \
                            dic['role'] == "destination":
                        ins1.destination = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and \
                            dic['role'] == "quantity":
                        ins1.amount = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and dic['role'] == "units":
                        ins1.units = dic['value']
                    elif dic['extractor'] == "RegexEntityExtractor" and dic['entity'] == "obj_to_be_shaken":
                        if ins1.obj_to_be_shaken is not None:
                            ins1.obj_to_be_shaken = dic['value']
                    elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "CARDINAL":
                        # if ins1.amount is not None:
                        ins1.amount = dic['value']
                    elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "QUANTITY":
                        # if ins1.amount is not None:
                        ins1.amount = dic['value']

                for key,value in compound_props['props'].items():
                    if key == ins1.obj_to_be_shaken:
                        ins1.obj_to_be_shaken_prop = prop_finder(value)
                    elif key == ins1.destination:
                        ins1.destination_prop = prop_finder(value)

                for key,value in compound_props['compounds_words'].items():
                    if value == ins1.obj_to_be_shaken:
                        ins1.obj_to_be_shaken_prop.update({'metadata':key})
                    elif value == ins1.destination:
                        ins1.destination_prop.update({'metadata':key})

                # act = action_verb_finder(intent,compound_props['verbs'])
                act, goal = testing_finder(intent=intent, source=ins1.obj_to_be_shaken, destination=ins1.destination,
                                            dix=compound_props['verbs'])
                ins1.action_verb = act
                ins1.goal = goal

                # if len(act) > 0:
                #     # if ins1.stuff in viscous and act not in slow_pouring:
                #     #     ins1.action_verb = 'drizzle'
                #     # else:
                #     ins1.action_verb = act
                # else:
                #     print("No POS Verb")
                #     common_verb = [word for word in compound_props['compounded_text'].split(" ")
                #                    if word in shakes][0]
                #     ins1.action_verb = common_verb

                motion, _ = motion_finder(intent=intent, source=ins1.obj_to_be_shaken, destination=ins1.destination,
                                             action_verb=ins1.action_verb,dix=compound_props['verbs'])

                ins1.motion = motion

            elif intent == "pick_up":
                ins1 = cores.Pickup()

                for dic in v:
                    if dic['extractor'] == "DIETClassifier" and dic['entity'] == "obj_to_be_picked":
                        ins1.obj_to_be_picked = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "location" and \
                            dic['role'] == "source":
                        ins1.source = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and \
                            dic['role'] == "quantity":
                        ins1.amount = dic['value']
                    elif dic['extractor'] == "DIETClassifier" and dic['entity'] == "amount" and dic['role'] == "units":
                        ins1.units = dic['value']
                    elif dic['extractor'] == "RegexEntityExtractor" and dic['entity'] == "obj_to_be_picked":
                        if ins1.obj_to_be_picked is not None:
                            ins1.obj_to_be_picked = dic['value']
                    elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "CARDINAL":
                        # if ins1.amount is not None:
                        ins1.amount = dic['value']
                    elif dic['extractor'] == "SpacyEntityExtractor" and dic['entity'] == "QUANTITY":
                        # if ins1.amount is not None:
                        ins1.amount = dic['value']

                for key,value in compound_props['props'].items():
                    if key == ins1.obj_to_be_picked:
                        ins1.obj_to_be_picked_prop = prop_finder(value)
                    elif key == ins1.source:
                        ins1.source_prop = prop_finder(value)

                for key,value in compound_props['compounds_words'].items():
                    if value == ins1.source:
                        ins1.source_prop.update({'metadata':key})
                    elif value == ins1.obj_to_be_picked:
                        ins1.obj_to_be_picked_prop.update({'metadata':key})

                act,goal = testing_finder(intent=intent,dix=compound_props["verbs"],source=ins1.source)
                ins1.action_verb = act
                ins1.goal = goal

                print("ToDo")

            elif intent == "put_down":
                print("ToDo")

            elif intent == "drop":
                print("ToDo")

    # ins1.print_params()
    return ins1
def testing_finder(intent=None,source=None,destination=None,stuff=None,dix=None):
    act = ""
    goal = ""
    if intent == "pouring":
        act = "pour"
        goal = "no spillage"
        if stuff in viscous:
            if 'ADV' in dix:
                advs = list(dix['ADV'].keys())
                found_adv = bool(set(advs) & set(adverbs))
                if found_adv:
                    print("viscous adverb found")
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        for vs in vbs:
                            if vs in slow_pouring:
                                act = vs
                                break
                            else:
                                act = "drizzle"
                    else:
                        act = "drizzle"
                    # goal.append("no spillage")
                    # goal = 'no spillage'
                else:
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        for vs in vbs:
                            if vs in slow_pouring:
                                act = vs
                                break
                            else:
                                act = "pour"
                    else:
                        act = "pour"
            else:
                if 'VERB' in dix:
                    vbs = list(dix['VERB'].keys())
                    # verb_list = slow_pouring + fast_pouring + shakes
                    for vs in vbs:
                        if vs in slow_pouring:
                            act = vs
                            break
                        else:
                            act = "pour"
                else:
                    act = "pour"

            if not destination is None:
                if 'batter' in stuff and 'pan' in destination:
                    # goal.append("")
                    goal = goal + " and " + "form a circular shape"
                if stemmer.stem(destination) in fires: goal = 'extinguish'
                if stemmer.stem(destination) in plants: goal = 'watering'

        elif stuff in nviscous:
            if 'ADV' in dix:
                advs = list(dix['ADV'].keys())
                found_adv = bool(set(advs) & set(adverbs))
                if found_adv:
                    print("nviscous adverb found")
                    # goal.append("no spillage")
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        for vs in vbs:
                            # verb_list = slow_pouring + fast_pouring + shakes
                            if vs in slow_pouring:
                                act = vs
                                break
                            else:
                                act = "pour"
                    else:
                        act = "pour"
                else:
                    # goal.append("no spillage")
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        # verb_list = slow_pouring+fast_pouring+shakes
                        for vs in vbs:
                            if vs in slow_pouring:
                                act = vs
                                break
                            else:
                                act = "pour"
                    else:
                        act = "pour"
            else:
                # goal.append("no spillage")
                if 'VERB' in dix:
                    vbs = list(dix['VERB'].keys())
                    # verb_list = slow_pouring + fast_pouring + shakes
                    for vs in vbs:
                        if vs in slow_pouring:
                            act = vs
                            break
                        else:
                            act = "pour"
                else:
                    act = "pour"

            if not destination is None:
                if stemmer.stem(destination) in fires: goal = 'extinguish'
                if stemmer.stem(destination) in plants: goal = 'watering'

            # if 'fire' in destination or 'flame' in destination:
            #     goal.append("extinguish")
            #
            # if 'plant' in destination or 'tree' in destination or 'flower' in destination or 'fruit' in destination:
            #     goal.append("watering")

        elif stuff in powdered:
            if 'ADV' in dix:
                advs = list(dix['ADV'].keys())
                found_adv = bool(set(advs) & set(adverbs))
                if found_adv:
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        for vs in vbs:
                            if vs in shakes:
                                act = vs
                                break
                            else:
                                act = "sprinkle"
                    else:
                        act = "sprinkle"
                    # goal.append("no spillage")
                else:
                    if 'VERB' in dix:
                        vbs = list(dix['VERB'].keys())
                        for vs in vbs:
                            if vs in shakes:
                                act = vs
                                break
                            else:
                                act = "sprinkle"
                    else:
                        act = "sprinkle"
            else:
                if 'VERB' in dix:
                    vbs = list(dix['VERB'].keys())
                    for vs in vbs:
                        if vs in shakes:
                            act = vs
                            break
                        else:
                            act = "sprinkle"
                else:
                    act = "sprinkle"

            if not destination is None:
                if stemmer.stem(destination) in fires: goal = 'extinguish'
                if stemmer.stem(destination) in plants: goal = 'watering'

    elif intent == "shake":
        act = "sprinkle"
        goal = "no spillage"
        if 'VERB' in dix:
            vbs = list(dix['VERB'].keys())
            for vs in vbs:
                if vs in shakes:
                    act = vs
                    break
                else:
                    act = "sprinkle"
        else:
            act = "sprinkle"

    elif intent == "pick_up":
        act = "lift"
        if 'VERB' in dix:
            vbs = list(dix['VERB'].keys())
            for vs in vbs:
                if vs in picks:
                    act = vs
                    break
                else:
                    act = "pick up"
        else:
            act = "pick up"

    return act,goal