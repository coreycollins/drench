
#violate pep8 so workflows can dump AWS-friendly JSON
#pylint: disable=invalid-name

import json
from drench_sdk.states import SucceedState, FailState

FINISH_END_NAME = 'finish'
FAILED_END_NAME = 'failed'

class TaxonomyError(Exception):
    """ error indicating non-matched taxonomies """
    def __init__(self, taxonomy_one, taxonomy_two, **kwargs):
        super(TaxonomyError, self).__init__(**kwargs)
        self.taxonomy_one = taxonomy_one
        self.taxonomy_two = taxonomy_two

    def __str__(self):
        return f'Taxonomies do not match:\n    {self.taxonomy_one!s}\n    {self.taxonomy_two!s}'

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, comment=None, timeout=None, version=None):


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

        if not transform.Next:
            transform.Next = FINISH_END_NAME

        transform.on_fail = FAILED_END_NAME

        if transform.Start:
            self.sfn['StartAt'] = transform.name

        self.sfn['States'] = {**self.sfn['States'], **transform.states()}

    def check_taxonomies(self):
        """make sure tanonomies match"""
        for transform in self.transforms.values():
            if transform.Next and transform.Next != FINISH_END_NAME:
                if transform.out_taxonomy != self.transforms[transform.Next].in_taxonomy:
                    raise TaxonomyError(transform.out_taxonomy, self.transforms[transform.Next].in_taxonomy)

    def toJson(self):
        """dump Worktransform to AWS Step Function JSON"""
        def encodeState(obj):
            """coerce object into dicts"""
            return dict((k, v) for k, v in obj.__dict__.items() if v)

        self.check_taxonomies()

        return json.dumps(self.sfn, default=encodeState, indent=4, sort_keys=True)
