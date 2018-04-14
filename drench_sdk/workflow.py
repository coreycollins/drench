'''workflows: chained and orchestrated sets of transforms'''

import json

from drench_resources import get_arn
from drench_sdk.states import State, SucceedState, FailState, TaskState, ChoiceState

UPDATE_END_NAME = '__update'
CHOICE_END_NAME = '__choice'
FINISH_END_NAME = '__finish'
FAILED_END_NAME = '__failed'

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
                Next=CHOICE_END_NAME,
                Retry=[{
                    'ErrorEquals': ['Lambda.Unknown'],
                    'IntervalSeconds': 30,
                    'MaxAttempts': 5,
                    'BackoffRate': 1.5
                }]
            ),
            CHOICE_END_NAME: ChoiceState(
                Choices=[
                    {
                        'Variable': f'$.result.status',
                        'StringEquals': 'pass',
                        'Next': FINISH_END_NAME
                    }
                ],
                Default=FAILED_END_NAME
            ),
            FINISH_END_NAME: SucceedState(),
            FAILED_END_NAME: FailState(),
        }

    def add_transform(self, transform):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if transform.name in [UPDATE_END_NAME, CHOICE_END_NAME, FINISH_END_NAME, FAILED_END_NAME]:
            raise Exception(f'The transform name {transform.name} is reserved')

        if not transform.Next:
            transform.Next = UPDATE_END_NAME

        transform._on_fail = UPDATE_END_NAME #pylint:disable=W0212

        if 'StartAt' not in self.sfn:
            self.sfn['StartAt'] = transform.name

        self.sfn['States'] = {**self.sfn['States'], **transform.states()}

    def as_dict(self):
        """ return state machine as a dict """
        def serialize(obj):
            if isinstance(obj, dict):
                return {k: serialize(v.__dict__)
                           if isinstance(v, State) else serialize(v)
                        for (k, v) in obj.items() if v}
            return obj

        return serialize(self.sfn)

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        return json.dumps(self.as_dict(), indent=4, sort_keys=True)
