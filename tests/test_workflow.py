#pylint:disable=missing-docstring
#pylint:disable=line-too-long
import pytest
from drench_sdk.workflow import WorkFlow, UPDATE_JOB
from drench_sdk.transforms import GlueTransform
import drench_sdk.config

def test_workflow():
    """main func"""
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    assert len(workflow.sfn['States']) == 11

def test_diff_version_workflow():
    """main func"""
    drench_sdk.config.SDK_VERSION = 'canary'
    workflow = WorkFlow(comment='test', timeout=60, version=1.1)
    assert workflow.sfn['States'][UPDATE_JOB].Resource.endswith(drench_sdk.config.SDK_VERSION)

def test_add_transform():
    workflow = WorkFlow()
    workflow.add_state(
        name='example-glue-job',
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    assert len(workflow.sfn['States']) == 17

def test_to_json():
    workflow = WorkFlow()
    workflow.add_state(
        name='example-glue-job',
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2
        )
    )

    w_f = workflow.as_dict()

    assert w_f['States']['example-glue-job']['Result']['type'] == 'glue'
    assert w_f['States']['example-glue-job.run_task']['Resource'].endswith(drench_sdk.config.SDK_VERSION)
    assert w_f['States']['example-glue-job.run_task']['Catch'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.wait']['Next'] == 'example-glue-job.check_task'
    assert w_f['States']['example-glue-job.check_task']['Catch'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.check_choice']['Choices'][0]['Next'] == 'example-glue-job.finish_choice'
    assert w_f['States']['example-glue-job.finish_choice']['Choices'][0]['Next'] == '__status_translate'
    assert w_f['States']['example-glue-job.finish_choice']['Default'] == '__status_translate'
    assert w_f['States']['__status_translate']['Default'] == '__status_failed'
    assert w_f['States']['__status_finished']['Result'] == 'finished'
    assert w_f['States']['__status_failed']['Result'] == 'failed'
    assert w_f['States']['__build_update']['Result']['path'] == '/jobs/$.job_id/state/$.result.status'
    assert w_f['States']['__update']['Next'] == '__end_selector'
    assert w_f['States']['__update']['Catch'][0]['Next'] == '__inject_sns_topic'
    assert w_f['States']['__inject_sns_topic']['Next'] == '__inject_sns_subject'
    assert w_f['States']['__inject_sns_subject']['Next'] == '__death_rattle'
    assert w_f['States']['__death_rattle']['Next'] == '__failed'
    assert w_f['States']['__end_selector']['Choices'][0]['Next'] == '__finished'
    assert w_f['States']['__end_selector']['Default'] == '__failed'
    assert w_f['States']['__failed']['Type'] == 'Fail'
    assert w_f['States']['__finished']['Type'] == 'Succeed'

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

    assert str(error.value) == 'The transform name __update is already in use'
