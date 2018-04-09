'''workflows: chained and orchestrated sets of transforms'''
#violate pep8 so workflows can dump AWS-friendly JSON
#pylint: disable=invalid-name

import json
from drench_sdk.states import SucceedState, FailState

FINISH_END_NAME = 'finish'
FAILED_END_NAME = 'failed'

DO_NOT_DICT_ENCODE = ['str', 'int']

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, pool_id=None, comment=None, timeout=None, version=None):

        self.pool_id = pool_id

        self.transforms = {}

        self.sfn = {}

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

    def addTransform(self, transform):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""
        self.transforms[transform.name] = transform
        transform.pool_id = self.pool_id

        if not transform.Next:
            transform.Next = FINISH_END_NAME

        transform.on_fail = FAILED_END_NAME

        if transform.Start:
            self.sfn['StartAt'] = transform.name

        self.sfn['States'] = {**self.sfn['States'], **transform.states()}

    def toJson(self):
        """dump Worktransform to AWS Step Function JSON"""
        def encodeState(obj):
            """coerce object into dicts"""
            try:
                return obj.to_json()
            except AttributeError:
                return dict((k, v) for k, v in obj.__dict__.items() if v)

        return json.dumps(self.sfn, default=encodeState, indent=4, sort_keys=True)
