"""Common states"""

#pylint:disable=too-few-public-methods
#pylint:disable=too-many-arguments
#pylint:disable=invalid-name

class State(object):
    """Base class for a state in the state machine."""
    def __init__(self, Type, InputPath=None, ResultPath=None, OutputPath=None, Next=None, Start=False, End=False):
        self.Type = Type
        self.Next = Next
        self.Start = Start
        self.End = End
        self.InputPath = InputPath
        self.ResultPath = ResultPath
        self.OutputPath = OutputPath

class SucceedState(State):
    """ Succeed state in the state machine."""
    def __init__(self):
        self.Type = "Succeed"

class FailState(State):
    """ Succeed state in the state machine."""
    def __init__(self, Cause=None, Error=None):
        self.Type = "Fail"
        self.Cause = Cause
        self.Error = Error

class PassState(State):
    """ Pass state in the state machine."""
    def __init__(self, Result=None, **kwargs):
        super(PassState, self).__init__(Type='Pass', **kwargs)
        self.Result = Result

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
    def __init__(self, Resource, Retry=None, Catch=None, Timeout=None, Heartbeat=None, **kwargs):
        super(TaskState, self).__init__(Type='Task', **kwargs)
        self.Resource = Resource
        self.Retry = Retry
        self.Catch = Catch
        self.Timeout = Timeout
        self.Heartbeat = Heartbeat
