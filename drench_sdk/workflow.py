'''workflows: chained and orchestrated sets of transforms'''

import json

from drench_resources import get_arn, get_resource
from drench_sdk.states import PassState, State, TaskState
from drench_sdk.transforms import Transform

BUILD_UPDATE = '__build_update'
UPDATE_END = '__update'
INJECT_SNS_TOPIC = '__inject_sns_topic'
INJECT_SNS_SUBJECT = '__inject_sns_subject'
DEATH_RATTLE = '__death_rattle'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, sdk_version='v1', comment=None, timeout=None, version=None):
        self.sfn = {}
        self.sdk_version = sdk_version

        if comment:
            self.sfn['Comment'] = comment

        if timeout:
            self.sfn['TimeoutSeconds'] = timeout

        if version:
            self.sfn['Version'] = version

        self.sfn['States'] = {
            BUILD_UPDATE: PassState(
                Result={
                    'body':{},
                    'method': 'PUT',
                    'path': '/jobs/$.job_id/state/$.result.status'
                },
                ResultPath='$.api_call',
                Next=UPDATE_END
            ),

            UPDATE_END: TaskState(
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
                        "Next": INJECT_SNS_TOPIC
                    }
                ]
            ),

            INJECT_SNS_TOPIC: PassState(
                Result=get_arn('sns', get_resource('drench-sdk-sfn-fail')),
                ResultPath='$.sns.topic_arn',
                Next=INJECT_SNS_SUBJECT
            ),

            INJECT_SNS_SUBJECT: PassState(
                Result='Drench Workflow communication failure',
                ResultPath='$.sns.subject',
                Next=DEATH_RATTLE
            ),

            DEATH_RATTLE: TaskState(
                Resource=get_arn('lambda', 'function:drench-sdk-send-sns'),
                End=True
            )
        }

    def add_state(self, name, state):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if name in [
                BUILD_UPDATE,
                UPDATE_END,
                INJECT_SNS_TOPIC,
                INJECT_SNS_SUBJECT,
                DEATH_RATTLE
        ]:
            raise Exception(f'The transform name {name} is reserved')

        if not state.Next:
            state.Next = BUILD_UPDATE

        if isinstance(state, Transform):
            self.sfn['States'] = {
                **self.sfn['States'],
                **state.states(
                    name=name,
                    on_fail=BUILD_UPDATE,
                    sdk_version=self.sdk_version
                )
            }
        elif isinstance(state, TaskState): #users adding TaskStates must know lambda version to call
            if not state.Catch:
                state.Catch = [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.result.status",
                        "Next": UPDATE_END
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
