"""Common states"""
import json

class State(object):
    """Base class for a state in the state machine."""

    def __init__(self, Name, Type, Next=None, End=False):
        self.Name = Name
        self.Type = Type
        self.Next = Next
        self.End = End

    def toJson(self):
        def encode_complex(obj):
            return dict((k, v) for k, v in obj.__dict__.iteritems() if v)

        return json.dumps(self, default=encode_complex)


class PassState(State):
    """ Pass state in the state machine."""
    def __init__(self, Result=None, ResultPath=None, **kwargs):
        super(PassState, self).__init__(Type='Pass', **kwargs)
        self.Result = Result
        self.ResultPath = ResultPath

class WaitState(State):
    """ Wait state in the state machine."""
    def __init__(self, Seconds=None, Timestamp=None, **kwargs):
        super(WaitState, self).__init__(Type='Wait', **kwargs)
        self.Seconds = Seconds
        self.Timestamp = Timestamp

        if (Seconds and Timestamp):
            raise "You can only set one of Seconds, Timestamp,"

class ChoiceState(State):
    """ Wait state in the state machine."""
    def __init__(self, Choices, Default=None, **kwargs):
        super(ChoiceState, self).__init__(Type='Choice', **kwargs)
        self.Choices = Choices
        self.Default = Default


class TaskState(State):
    """docstring for ."""
    def __init__(self, Resource, ResultPath=None, Retry=None, Catch=None, Timeout=None, Heartbeat=None, **kwargs):
        super(TaskState, self).__init__(Type='Task', **kwargs)
        self.Resource = Resource
        self.ResultPath = ResultPath
        self.Retry = Retry
        self.Catch = Catch
        self.Timeout = Timeout
        self.Heartbeat = Heartbeat
