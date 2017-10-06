import json

class StateMachine(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, Comment=None, TimeoutSeconds=None, Version=None):
        self.States = {}

        self.Comment = Comment
        self.TimeoutSeconds = TimeoutSeconds
        self.Version = Version

        # Don't implicitly start anywhere
        self.StartAt = None

    def addFlow(self, Flow, Start=False):
        self.States.update(Flow.states())
        if (Start):
            self.StartAt = Flow.Name

    def addState(self, Name, State, Start=False):
        self.States.update({Name:State})
        if (Start):
            self.StartAt = Name

    def toJson(self):
        def encodeState(obj):
            return dict((k, v) for k, v in obj.__dict__.iteritems() if v)

        return json.dumps(self, default=encodeState, indent=4, sort_keys=True)
