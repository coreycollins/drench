"""workflows are a wrapper for aws step fucntions"""

# TODO: use pep8 for object names and write JSON spec?
#pylint: disable=invalid-name

import json
from states import SucceedState, FailState

FINISH_STATE_NAME = 'finish'
FAILED_STATE_NAME = 'failed'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, Comment=None, TimeoutSeconds=None, Version=None):
        self.States = {
            FINISH_STATE_NAME: SucceedState(),
            FAILED_STATE_NAME: FailState()
        }

        self.Comment = Comment
        self.TimeoutSeconds = TimeoutSeconds
        self.Version = Version

        # Don't implicitly start anywhere
        self.StartAt = None

    def addFlow(self, Flow):
        """ adds flow's states to workflow, overwrites in the case of name colissions"""

        if not Flow.on_succeed:
            Flow.on_succeed = FINISH_STATE_NAME

        Flow.OnFail = FAILED_STATE_NAME

        if Flow.start:
            self.StartAt = Flow.name

        # TODO: check for colision
        self.States = {**self.States, **Flow.states()}

    def toJson(self):
        """dump Workflow to AWS Step Function JSON"""
        def encodeState(obj):
            """lambda object into dicts"""
            return dict((k, v) for k, v in obj.__dict__.items() if v)

        return json.dumps(self, default=encodeState, indent=4, sort_keys=True)
