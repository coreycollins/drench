'''workflows: chained and orchestrated sets of transforms'''

import json

from drench_sdk.utils import get_arn
from drench_sdk.states import  ChoiceState, FailState, PassState, SucceedState, State, TaskState
from drench_sdk.transforms import Transform

SETUP = '__setup'
FAILED = '__failed'
FINISHED = '__finished'
END_SELECTOR = '__end_selector'
STATUS_TRANSLATE = '__status_translate'
STATUS_RUNNING = '__status_running'
STATUS_FINISHED = '__status_finished'
STATUS_FAILED = '__status_failed'
UPDATE_RUNNING = '__update_running'
UPDATE_DONE = '__update_done'
INJECT_SNS_TOPIC = '__inject_sns_topic'
INJECT_SNS_SUBJECT = '__inject_sns_subject'
DEATH_RATTLE = '__death_rattle'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, comment=None, timeout=None, version=None):
        self.sfn = {}
        from drench_sdk.config import SDK_VERSION

        if comment:
            self.sfn['Comment'] = comment

        if timeout:
            self.sfn['TimeoutSeconds'] = timeout

        if version:
            self.sfn['Version'] = version

        self.sfn['StartAt'] = STATUS_RUNNING

        self.sfn['States'] = {
            STATUS_RUNNING: PassState(
                Result='running',
                ResultPath='$.result.status',
                Next=UPDATE_RUNNING
            ),
            UPDATE_RUNNING: TaskState(
                Resource=get_arn('lambda', f'function:{SDK_VERSION}-drench-sdk-send-sns'),
                Next=END_SELECTOR, # This SHOULD get updated before generation
                ResultPath='$.sns.result',
                Retry=[{
                    'ErrorEquals': ['Lambda.Unknown'],
                    'IntervalSeconds': 30,
                    'MaxAttempts': 5,
                    'BackoffRate': 1.5
                }]
            ),
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
                Next=UPDATE_DONE
            ),

            STATUS_FAILED: PassState(
                Result='failed',
                ResultPath='$.result.status',
                Next=UPDATE_DONE
            ),

            UPDATE_DONE: TaskState(
                Resource=get_arn('lambda', f'function:{SDK_VERSION}-drench-sdk-send-sns'),
                Next=END_SELECTOR,
                ResultPath='$.sns.result',
                Retry=[{
                    'ErrorEquals': ['Lambda.Unknown'],
                    'IntervalSeconds': 30,
                    'MaxAttempts': 5,
                    'BackoffRate': 1.5
                }]
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
            FINISHED: SucceedState(),
            FAILED: FailState()
        }

    def add_state(self, name, state, start=False):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if name in self.sfn['States'].keys():
            raise Exception(f'The transform name {name} is already in use')

        if start:
            self.sfn['States'][UPDATE_RUNNING].Next = name

        if not state.Next:
            state.Next = STATUS_TRANSLATE

        if isinstance(state, Transform):
            self.sfn['States'] = {
                **self.sfn['States'],
                **state.states(
                    name=name,
                    on_fail=STATUS_TRANSLATE
                )
            }
        elif isinstance(state, TaskState): #users adding TaskStates must know lambda version to call
            if not state.Catch:
                state.Catch = [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.result.status",
                        "Next": STATUS_TRANSLATE
                    }
                ]
            self.sfn['States'][name] = state


    def as_dict(self):
        """ return state machine as a dict """
        def serialize(obj):
            '''coerce objects to dict as necessary'''
            if isinstance(obj, dict):
                return {k: serialize(v.__dict__)
                           if isinstance(v, State) else serialize(v)
                        for (k, v) in obj.items() if v}
            return obj

        if self.sfn['States'][UPDATE_RUNNING].Next == END_SELECTOR:
            raise Exception('The workflow does not have a start state defined.')

        return serialize(self.sfn)

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        return json.dumps(self.as_dict(), sort_keys=True)
