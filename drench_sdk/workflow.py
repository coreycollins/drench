'''workflows: chained and orchestrated sets of transforms'''

import json

from drench_sdk.utils import get_arn
from drench_sdk.states import  ChoiceState, FailState, PassState, SucceedState, State, TaskState
from drench_sdk.transforms import Transform

FAILED = '__failed'
FINISHED = '__finished'
END_SELECTOR = '__end_selector'
STATUS_TRANSLATE = '__status_translate'
STATUS_FINISHED = '__status_finished'
STATUS_FAILED = '__status_failed'
BUILD_UPDATE = '__build_update'
UPDATE_JOB = '__update'
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
            STATUS_TRANSLATE: ChoiceState(
                Choices=[
                    {
                        'Variable': f'$.result.status',
                        'StringEquals': 'pass',
                        'Next': STATUS_FINISHED
                    }
                ],
                Default=STATUS_FAILED
            ),

            STATUS_FINISHED: PassState(
                Result='finished',
                ResultPath='$.result.status',
                Next=BUILD_UPDATE
            ),

            STATUS_FAILED: PassState(
                Result='failed',
                ResultPath='$.result.status',
                Next=BUILD_UPDATE
            ),

            BUILD_UPDATE: PassState(
                Result={
                    'body':{},
                    'method': 'PUT',
                    'path': '/jobs/$.job_id/state/$.result.status'
                },
                ResultPath='$.api_call',
                Next=UPDATE_JOB
            ),

            UPDATE_JOB: TaskState(
                Resource=get_arn('lambda', f'function:drench-sdk-call-api:{sdk_version}'),
                Next=END_SELECTOR,
                ResultPath='$.api_result',
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

            END_SELECTOR: ChoiceState(
                Choices=[
                    {
                        'Variable': '$.result.status',
                        'StringEquals': 'finished',
                        'Next': FINISHED
                    }
                ],
                Default=FAILED
            ),

            INJECT_SNS_TOPIC: PassState(
                Result=get_arn('lambda', f'function:drench-sdk-send-sns:{sdk_version}'),
                ResultPath='$.sns.topic_arn',
                Next=INJECT_SNS_SUBJECT
            ),

            INJECT_SNS_SUBJECT: PassState(
                Result='Drench Workflow communication failure',
                ResultPath='$.sns.subject',
                Next=DEATH_RATTLE
            ),

            DEATH_RATTLE: TaskState(
                Resource=get_arn('lambda', f'function:drench-sdk-send-sns:{sdk_version}'),
                Next=FAILED
            ),

            FINISHED: SucceedState(),
            FAILED: FailState()
        }

    def add_state(self, name, state):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if name in self.sfn['States'].keys():
            raise Exception(f'The transform name {name} is already in use')

        if not state.Next:
            state.Next = STATUS_TRANSLATE

        if isinstance(state, Transform):
            self.sfn['States'] = {
                **self.sfn['States'],
                **state.states(
                    name=name,
                    on_fail=STATUS_TRANSLATE,
                    sdk_version=self.sdk_version
                )
            }
        elif isinstance(state, TaskState): #users adding TaskStates must know lambda version to call
            if not state.Catch:
                state.Catch = [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.result.status",
                        "Next": UPDATE_JOB
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
