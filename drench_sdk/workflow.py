'''workflows: chained and orchestrated sets of transforms'''

import json
from drench_sdk.states import SucceedState, FailState, TaskState, ChoiceState
from drench_sdk.resources import Resources

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
                Resource=Resources.get_arn('lambda', f'function:drench_sdk_update_job'),
                End=CHOICE_END_NAME,
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

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        def encode_state(obj):
            """coerce object into dicts"""
            try:
                return obj.to_json()
            except AttributeError:
                return dict((k, v) for k, v in obj.__dict__.items() if v)

        return json.dumps(self.sfn, default=encode_state, indent=4, sort_keys=True)
