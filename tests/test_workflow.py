#pylint:disable=missing-docstring
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import GlueTransform

def test_workflow():
    """main func"""
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)

    assert len(workflow.sfn['States']) == 3

def test_add_transform():
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    workflow.add_transform(
        GlueTransform(
            name='example-glue-job',
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    assert len(workflow.sfn['States']) == 10
