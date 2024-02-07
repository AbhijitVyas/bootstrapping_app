class Pouring:
    def __init__(self, source=None, source_prop={}, destination="", destination_prop={}, stuff="",
                 stuff_prop={}, amount="", units="", action_verb="", motion="", goal=""):
        self.source = source
        self.source_prop = source_prop
        self.destination = destination
        self.destination_prop = destination_prop
        self.stuff = stuff
        self.stuff_prop = stuff_prop
        self.amount = amount
        self.units = units
        self.action_verb = action_verb
        self.motion = motion
        self.goal = goal

    def print_params(self):
        dix = {
            'source':self.source,
            'source_prop':self.source_prop,
            'destination':self.destination,
            'destination_prop':self.destination_prop,
            'substance':self.stuff,
            'substance_prop':self.stuff_prop,
            'amount':self.amount,
            'units':self.units,
            'action_verb':self.action_verb,
            'motion': self.motion,
            'goal': self.goal
        }
        # print(dix)
        return dix
class Shake:
    def __init__(self, obj_to_be_shaken="", obj_to_be_shaken_prop={}, destination="",
                 destination_prop={}, amount="", units="", action_verb="", motion="", goal=""):
        self.obj_to_be_shaken = obj_to_be_shaken
        self.obj_to_be_shaken_prop = obj_to_be_shaken_prop
        self.destination = destination
        self.destination_prop = destination_prop
        self.amount = amount
        self.units = units
        self.action_verb = action_verb
        self.motion = motion
        self.goal = goal

    def print_params(self):
        dix = {
            'obj_to_be_shaken':self.obj_to_be_shaken,
            'obj_to_be_shaken_prop':self.obj_to_be_shaken,
            'destination':self.destination,
            'destination_prop':self.destination_prop,
            'amount':self.amount,
            'units':self.units,
            'action_verb':self.action_verb,
            'motion': self.motion,
            'goal': self.goal
        }
        print(dix)
        return dix
class Pickup:
    def __init__(self, obj_to_be_picked="", obj_to_be_picked_prop={}, source="",
                 source_prop={},amount="",units="",action_verb="", motion="", goal=""):
        self.obj_to_be_picked = obj_to_be_picked
        self.obj_to_be_picked_prop = obj_to_be_picked_prop
        self.source = source
        self.source_prop = source_prop
        self.amount = amount
        self.units = units
        self.action_verb = action_verb
        self.motion = motion
        self.goal = goal

    def print_params(self):
        dix = {
            'obj_to_be_picked':self.obj_to_be_picked,
            'obj_to_be_picked_prop':self.obj_to_be_picked_prop,
            'source':self.source,
            'source_prop':self.source_prop,
            'amount':self.amount,
            'units':self.units,
            'action_verb':self.action_verb,
            'motion': self.motion,
            'goal': self.goal
        }
        print(dix)
        return dix

class Putdown:
    def __init__(self, obj_to_be_put="", obj_to_be_put_prop= "", destination="",
                 destination_prop="",action_verb="", motion="", goal=""):
        self.obj_to_be_put = obj_to_be_put
        self.obj_to_be_put_prop = obj_to_be_put_prop
        self.destination = destination
        self.destination_prop = destination_prop
        self.action_verb = action_verb
        self.motion = motion
        self.goal = goal

    def print_params(self):
        dix = {
            'obj_to_be_put':self.obj_to_be_put,
            'obj_to_be_put_prop':self.obj_to_be_put_prop,
            'destination':self.destination,
            'destination_prop':self.destination_prop,
            'action_verb':self.action_verb,
            'motion': self.motion,
            'goal': self.goal
        }
        print(dix)
        return dix

class Drop:
    def __init__(self, obj_to_drop="", obj_to_drop_prop= "",action_verb="", motion="", goal=""):
        self.obj_to_drop = obj_to_drop
        self.obj_to_drop_prop = obj_to_drop_prop
        self.action_verb = action_verb
        self.motion = motion
        self.goal = goal

    def print_params(self):
        dix = {
            'obj_to_drop':self.obj_to_drop,
            'obj_to_drop_prop':self.obj_to_drop_prop,
            'action_verb':self.action_verb,
            'motion': self.motion,
            'goal': self.goal
        }
        print(dix)
        return dix