"""workflows are a wrapper for aws step fucntions"""
#violate pep8 so workflows can dump AWS-friendly JSON
#pylint: disable=invalid-name

import json
from states import SucceedState, FailState

FINISH_END_NAME = 'finish'
FAILED_END_NAME = 'failed'

class TaxonomyMismatchError(BaseException):
    """ error indicating non-matched taxonomies """
    def __init__(self, **kwargs):
        super(TaxonomyMismatchError, self).__init__(**kwargs)

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, comment=None, timeout=None, version=None):


        self.flows = {}

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

    def addFlow(self, Flow):
        """ adds flow's states to workflow, overwrites in the case of name colissions"""
        self.flows[Flow.name] = Flow

        if not Flow.on_succeed:
            Flow.on_succeed = FINISH_END_NAME

        Flow.OnFail = FAILED_END_NAME

        if Flow.start:
            self.sfn['StartAt'] = Flow.name

        self.sfn['States'] = {**self.sfn['States'], **Flow.states()}

    def check_taxonomies(self):
        """make sure tanonomies match"""
        for flow in self.flows.values():
            if flow.on_succeed and flow.on_succeed != FINISH_END_NAME:
                if flow.out_taxonomy != self.flows[flow.on_succeed].in_taxonomy:
                    raise TaxonomyMismatchError()

    def toJson(self):
        """dump Workflow to AWS Step Function JSON"""
        def encodeState(obj):
            """coerce object into dicts"""
            return dict((k, v) for k, v in obj.__dict__.items() if v)

        self.check_taxonomies()

        return json.dumps(self.sfn, default=encodeState, indent=4, sort_keys=True)
