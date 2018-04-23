'''workflows: chained and orchestrated sets of transforms'''

import json

from drench_resources import get_arn, get_resource
from drench_sdk.states import PassState, State, TaskState
from drench_sdk.transforms import Transform

UPDATE_END_NAME = '__update'
INJECT_SNS_TOPIC_NAME = '__inject_sns_topic'
INJECT_SNS_SUBJECT_NAME = '__inject_sns_subject'
DEATH_RATTLE_NAME = '__death_rattle'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, comment=None, timeout=None, version=None):
        self.sfn = {}

        if comment:
            self.sfn['Comment'] = comment

        if timeout:
            self.sfn['TimeoutSeconds'] = timeout

        if version:
            self.sfn['Version'] = version

        self.sfn['States'] = {
            UPDATE_END_NAME: TaskState(
                Resource=get_arn('lambda', f'function:drench-sdk-update-job'),
                End=True,
                Retry=[{
                    'ErrorEquals': ['Lambda.Unknown'],
                    'IntervalSeconds': 30,
                    'MaxAttempts': 5,
                    'BackoffRate': 1.5
                }],
                Catch=[
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.sns.message",
                        "Next": INJECT_SNS_TOPIC_NAME
                    }
                ]
            ),

            INJECT_SNS_TOPIC_NAME: PassState(
                Result=get_arn('sns', get_resource('drench-sdk-sfn-fail')),
                ResultPath='$.sns.topic_arn',
                Next=INJECT_SNS_SUBJECT_NAME
            ),

            INJECT_SNS_SUBJECT_NAME: PassState(
                Result='Drench Workflow communication failure',
                ResultPath='$.sns.subject',
                Next=DEATH_RATTLE_NAME
            ),

            DEATH_RATTLE_NAME: TaskState(
                Resource=get_arn('lambda', 'function:drench-sdk-send-sns'),
                End=True
            )
        }

    def add_state(self, name, state):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if name in [
                UPDATE_END_NAME,
                INJECT_SNS_TOPIC_NAME,
                INJECT_SNS_SUBJECT_NAME,
                DEATH_RATTLE_NAME
        ]:
            raise Exception(f'The transform name {name} is reserved')

        if not state.Next:
            state.Next = UPDATE_END_NAME

        if isinstance(state, Transform):
            state._on_fail = UPDATE_END_NAME #pylint:disable=W0212
            self.sfn['States'] = {**self.sfn['States'], **state.states(name)}
        elif isinstance(state, TaskState):
            if not state.Catch:
                state.Catch = [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.result.status",
                        "Next": UPDATE_END_NAME
                    }
                ]
            self.sfn['States'][name] = state

        if 'StartAt' not in self.sfn:
            self.sfn['StartAt'] = name

    def as_dict(self):
        """ return state machine as a dict """
        def serialize(obj):
            '''coerce objects to dict as necessary'''
            if isinstance(obj, dict):
                return {k: serialize(v.__dict__)
                           if isinstance(v, State) else serialize(v)
                        for (k, v) in obj.items() if v}
            return obj

        return serialize(self.sfn)

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        return json.dumps(self.as_dict(), indent=4, sort_keys=True)
