"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
#from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform
from drench_sdk.transforms import GlueTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    #workflow.addTransform(
    #    QueryTransform(
    #        name='example-query-transform',
    #        database='some_db',
    #        QueryString='SELECT id, name FROM some_table LIMIT 100;',
    #        Next='example-batch-transform',
    #        Start=True
    #    )
    #)

    #workflow.addTransform(
    #    BatchTransform(
    #        name='example-batch-transform',
    #        job_queue='test-queue',
    #        job_definition='sap-job-execution',
    #        parameters={
    #            'job': '$.params.job'
    #        },
    #        Next='example-glue-transform',
    #    )
    #)

    workflow.addTransform(
        GlueTransform(
            name='example-glue-transform',
            Jobname='example-job-def',
            AllocatedCapacity=2,
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    example_workflow()
