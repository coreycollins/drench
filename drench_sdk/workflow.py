"""workflows are a wrapper for aws step fucntions"""

# TODO: use pep8 for object names and write JSON spec?
#pylint: disable=invalid-name

import json
from flows import SNSFlow
from states import SucceedState, FailState

FINISH_FLOW_NAME = 'SuccessSend'
FINISH_END_NAME = 'finish'
FINISH_SUBJ = 'Job succeeded'

FAILED_FLOW_NAME = 'FailSend'
FAILED_END_NAME = 'failed'
FAILED_SUBJ = 'Job Failed'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, Comment=None, TimeoutSeconds=None, Version=None, topic_arn=None):

        self.Comment = Comment
        self.TimeoutSeconds = TimeoutSeconds
        self.Version = Version
        self.topic_arn = topic_arn

        self.States = {
            FINISH_END_NAME: SucceedState(),
            FAILED_END_NAME: FailState(),
        }

        if topic_arn:
            self.States = {
                **self.States,
                **{
                    FINISH_FLOW_NAME: SNSFlow(
                        name=FINISH_FLOW_NAME,
                        TopicArn=topic_arn,
                        Subject=FINISH_SUBJ,
                        Message=FINISH_SUBJ,
                        on_succeed=FINISH_END_NAME,
                        in_taxonomy=None,
                        out_taxonomy=None
                    ),

                    FAILED_FLOW_NAME: SNSFlow(
                        name=FAILED_FLOW_NAME,
                        TopicArn=topic_arn,
                        Subject=FAILED_SUBJ,
                        Message=FAILED_SUBJ,
                        on_succeed=FAILED_END_NAME,
                        in_taxonomy=None,
                        out_taxonomy=None
                    ),
                }
            }

        self.Comment = Comment
        self.TimeoutSeconds = TimeoutSeconds
        self.Version = Version

        # Don't implicitly start anywhere
        self.StartAt = None

    def addFlow(self, Flow):
        """ adds flow's states to workflow, overwrites in the case of name colissions"""

        if not Flow.on_succeed:
            Flow.on_succeed = FINISH_FLOW_NAME if self.topic_arn else FINISH_END_NAME

        Flow.OnFail = FAILED_FLOW_NAME if self.topic_arn else FAILED_END_NAME

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
