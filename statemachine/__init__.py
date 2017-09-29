import json

class StateMachine(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self):
        self.machine = {}

    def addFlow(self, flow):
        self.machine.update(flow.states())

    def addState(self, Name, State):
        dic = {}
        dic[Name] = State
        self.machine.update(dic)

    def toJson(self):
        def encodeState(obj):
            return dict((k, v) for k, v in obj.__dict__.iteritems() if v)

        return json.dumps(self.machine, default=encodeState, indent=4, sort_keys=True)
