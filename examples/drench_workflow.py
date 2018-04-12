"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.add_transform(
        QueryTransform(
            name='example-query-transform',
            database='some_db',
            query_string='SELECT id, name FROM some_table LIMIT 100;',
            run_next='example-batch-transform',
            Start=True
        )
    )

    workflow.add_transform(
        BatchTransform(
            name='example-batch-transform',
            job_queue='test-queue',
            job_definition='sap-job-execution',
            parameters={
                'job': '$.params.job'
            },
            run_next='example-glue-transform',
        )
    )

    workflow.add_transform(
        GlueTransform(
            name='example-glue-transform',
            job_name='example-job-def',
            allocated_capacity=2,
        )
    )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
