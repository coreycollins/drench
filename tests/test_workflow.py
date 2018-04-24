#pylint:disable=missing-docstring
import json
import pytest
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import GlueTransform

def test_workflow():
    """main func"""
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)

    assert len(workflow.sfn['States']) == 4

def test_add_transform():
    workflow = WorkFlow('canary', comment='test', timeout=60, version=1.1)
    workflow.add_state(
        name='example-glue-job',
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    assert len(workflow.sfn['States']) == 11

def test_to_json():
    workflow = WorkFlow()
    workflow.add_state(
        name='example-glue-job',
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    w_f = json.loads(workflow.to_json())

    assert w_f['States']['example-glue-job.2.run']['Resource'].endswith(':v1')

def test_reserved_name():
    with pytest.raises(Exception) as error:
        workflow = WorkFlow()
        workflow.add_state(
            name='__update',
            state=GlueTransform(
                job_name='example-job-def',
                allocated_capacity=2
            )
        )

    assert str(error.value) == 'The transform name __update is reserved'
