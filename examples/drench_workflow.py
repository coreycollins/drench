"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow()

    workflow.add_transform(
        QueryTransform(
            name='example-query-transform',
            database='some_db',
            query_string='SELECT id, name FROM some_table LIMIT 100;',
            Next='example-batch-transform',
            Start=True
        )
    )

    workflow.add_transform(
        BatchTransform(
            name='example-batch-transform',
            job_queue='test-queue',
            job_definition='sap-job-execution',
            parameters={
                '--flag': 'some-value'
            },
            Next='example-glue-transform',
        )
    )

    workflow.add_transform(
        GlueTransform(
            name='example-glue-transform',
            job_name='example-job-def',
            allocated_capacity=2,
            arguments={
                '--command-line-switch': True
            }
        )
    )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
