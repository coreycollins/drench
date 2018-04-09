"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.addTransform(
        BatchTransform(
            name='example-batch-transform',
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
            Jobname='example-job-def',
            AllocatedCapacity=2
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    example_workflow()
