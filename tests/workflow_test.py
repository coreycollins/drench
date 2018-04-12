#pylint:disable=missing-docstring
import json
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import GlueTransform

def test_workflow():
    """main func"""
    workflow = WorkFlow(account_id=1234, comment='test', timeout=60, version=1.1)

    assert len(workflow.sfn['States']) == 4

def test_add_transform():
    workflow = WorkFlow(account_id=1234, comment='test', timeout=60, version=1.1)
    workflow.add_transform(
        GlueTransform(
            name='example-glue-job',
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    assert len(workflow.sfn['States']) == 11

def test_to_json():
    workflow = WorkFlow(account_id=1234, comment='test', timeout=60, version=1.1)
    correct_sfn = ''
    with open('tests/correct.json') as file_handle:
        correct_sfn = file_handle.read()

    assert json.loads(workflow.to_json()) == json.loads(correct_sfn)
