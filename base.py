# rasa run --enable-api --debug
from scripts import preprocessors
from scripts import call_rasa
from scripts import postprocessings

def main(inputs: str):
    flag = False
    error = ""
    results = None
    intents = ""
    # user_input = input("Enter an NL instruction: ")
    # print("You entered:", user_input.lower())
    
    compound_props = preprocessors.preprocessing(inputs.lower())
    print("processsed input: ",compound_props['compounds_words'])

    try:
        rasa_out = call_rasa.query_rasa(inputs.lower())
        # if rasa_out['intent']['name'] in ['pick_up','drop','put_down']:
        print("RASA output: ", rasa_out)
        # else:
        print("Intent: ", rasa_out['intent']['name'])
        intents = rasa_out['intent']['name']
    except:
        flag = True
        print("RASA server is not up and running")
        error = "RASA server is not up and running"

    try:
        instance = postprocessings.postprocess(rasa_out, compound_props)
        if instance is not None:
            # print("Final Output")
            results = instance.print_params()
        else:
            flag = True
            print("Post processed instance is None")
            error = "Post processed instance is None"
    except:
        flag = True
        print("Post Process error")
        error = "Post Process error"

    if not flag:
        return intents,results
    else:
        return intents,{'error':error}

    # continues = input("Continue (y/n): ")
    # if continues=="y":
    #     return True
    # else:
    #     return False

if __name__ == "__main__":
    main(inputs=None)
    # flag = True
    # while flag:
    #     flag = main()