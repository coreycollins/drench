#pylint:disable=missing-docstring
#pylint:disable=line-too-long
import pytest
from drench_sdk.workflow import WorkFlow, UPDATE_DONE
from drench_sdk.transforms import LambdaTransform, GlueTransform
import drench_sdk.config

def test_workflow():
    """main func"""
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    assert len(workflow.sfn['States']) == 9

def test_diff_version_workflow():
    """main func"""
    drench_sdk.config.SDK_VERSION = 'canary'
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    assert drench_sdk.config.SDK_VERSION in workflow.sfn['States'][UPDATE_DONE].Resource

def test_lambda_workflow():
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    workflow.add_state(
        name='example',
        start=True,
        state=LambdaTransform(
            resource_arn='arn:test',
            parameters={
                'workflow': 'test'
            }
        )
    )

    assert len(workflow.sfn['States']) == 11
    w_f = workflow.as_dict()
    assert w_f['States']['example.run']['Resource'] == 'arn:test'

def test_add_transform():
    workflow = WorkFlow()
    workflow.add_state(
        name='example-glue-job',
        start=True,
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    assert len(workflow.sfn['States']) == 15

def test_to_json():
    workflow = WorkFlow()
    workflow.add_state(
        name='example-glue-job',
        start=True,
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    w_f = workflow.as_dict()

    assert w_f['States']['example-glue-job']['Result']['type'] == 'glue'
    assert drench_sdk.config.SDK_VERSION in w_f['States']['example-glue-job.run_task']['Resource']
    assert w_f['States']['example-glue-job.run_task']['Catch'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.wait']['Next'] == 'example-glue-job.check_task'
    assert w_f['States']['example-glue-job.check_task']['Catch'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.check_choice']['Choices'][0]['Next'] == 'example-glue-job.finish_choice'
    assert w_f['States']['example-glue-job.finish_choice']['Choices'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.finish_choice']['Default'] == '__status_translate'
    assert w_f['States']['__status_translate']['Default'] == '__status_failed'
    assert w_f['States']['__status_finished']['Result'] == 'finished'
    assert w_f['States']['__status_failed']['Result'] == 'failed'
    assert w_f['States']['__update_running']['Next'] == 'example-glue-job'
    assert w_f['States']['__update_done']['Next'] == '__end_selector'
    assert w_f['States']['__end_selector']['Choices'][0]['Next'] == '__finished'
    assert w_f['States']['__end_selector']['Default'] == '__failed'
    assert w_f['States']['__failed']['Type'] == 'Fail'
    assert w_f['States']['__finished']['Type'] == 'Succeed'

def test_reserved_name():
    with pytest.raises(Exception) as error:
        workflow = WorkFlow()
        workflow.add_state(
            name='__update_done',
            start=True,
            state=GlueTransform(
                job_name='example-job-def',
                allocated_capacity=2
            )
        )

    assert str(error.value) == 'The transform name __update_done is already in use'
