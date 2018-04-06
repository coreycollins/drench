"""example/test script for developing drench_sdk"""
import json
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform
from drench_sdk.taxonomy import Taxonomy

def test_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.addTransform(
        BatchTransform(
            name='example-batch-flow',
            input_data={
                'path':'s3://some_bucket/pool_id/job_id',
                'taxonomy':Taxonomy(
                    format_type='csv',
                    fields=[
                        {'name':'name', 'field_type':'string'},
                        {'name':'id', 'field_type':'integer'}
                    ]
                    ),
                },
            output_data={
                'path':'s3://some_bucket/pool_id/job_id',
                'taxonomy':Taxonomy(
                    format_type='csv',
                    fields=[
                        {'name':'name', 'field_type':'string'},
                        {'name':'id', 'field_type':'integer'}
                    ]
                    ),
                },
            job_queue='test-queue',
            job_definition='sap-job-execution',
            parameters={
                'job': '$.params.job'
            },
            Next='example-glue-job',
            Start=True
        )
    )

    workflow.addTransform(
        GlueTransform(
            name='example-glue-job',
            input_data={
                'path':'s3://some_bucket/pool_id/job_id',
                'taxonomy':Taxonomy(
                    format_type='csv',
                    fields=[
                        {'name':'name', 'field_type':'string'},
                        {'name':'id', 'field_type':'integer'}
                    ]
                    ),
                },
            output_data={
                'path':'s3://some_bucket/pool_id/job_id',
                'taxonomy':Taxonomy(
                    format_type='csv',
                    fields=[
                        {'name':'name', 'field_type':'string'},
                        {'name':'id', 'field_type':'integer'}
                    ]
                    ),
                },
            Jobname='example-job-def',
            AllocatedCapacity=2
        )
    )

    correct_sfn = ''
    with open('tests/correct.json') as file_handle:
        correct_sfn = file_handle.read()

    assert json.loads(workflow.toJson()) == json.loads(correct_sfn)
