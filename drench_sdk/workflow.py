'''workflows: chained and orchestrated sets of transforms'''

import json
from drench_sdk.states import SucceedState, FailState, ChoiceState

FINISH_END_NAME = 'finish'
FAILED_END_NAME = 'failed'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, pool_id, comment=None, timeout=None, version=None):

        self.pool_id = pool_id

        self.sfn = {"StartAt": "check_job_id",}
        self.first_transform = None

        if comment:
            self.sfn['Comment'] = comment

        if timeout:
            self.sfn['TimeoutSeconds'] = timeout

        if version:
            self.sfn['Version'] = version

        self.sfn['States'] = {
            FINISH_END_NAME: SucceedState(),
            FAILED_END_NAME: FailState(),
        }

    def add_check_states(self):
        '''add initial states to fail if missing needed input'''

        check_states = {
            "check_job_id": ChoiceState(
                Choices=[
                    {
                        'Variable': '$.job_id',
                        'StringEquals': '',
                        'Next': FAILED_END_NAME
                    },
                ],
                Default=self.first_transform
            )
        }

        self.sfn['States'] = {**self.sfn['States'], **check_states}


    def add_transform(self, transform):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if not self.first_transform:
            self.first_transform = transform.name


        if not transform.run_next:
            transform.run_next = FINISH_END_NAME

        transform.on_fail = FAILED_END_NAME

        self.sfn['States'] = {**self.sfn['States'], **transform.states()}

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        def encode_state(obj):
            """coerce object into dicts"""
            try:
                return obj.to_json()
            except AttributeError:
                return dict((k, v) for k, v in obj.__dict__.items() if v)

        self.add_check_states()
        return json.dumps(self.sfn, default=encode_state, indent=4, sort_keys=True)
