"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform
from drench_sdk.taxonomy import Taxonomy

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.addTransform(
        QueryTransform(
            name='example-query-transform',
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
            database='some_db',
            QueryString='SELECT id, name FROM some_table LIMIT 100;',
            Next='example-batch-transform',
            Start=True
        )
    )

    workflow.addTransform(
        BatchTransform(
            name='example-batch-transform',
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
            Next='example-glue-transform',
        )
    )

    workflow.addTransform(
        GlueTransform(
            name='example-glue-transform',
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

    print(workflow.toJson())

if __name__ == '__main__':
    example_workflow()
