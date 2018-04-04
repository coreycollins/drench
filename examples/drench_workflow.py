"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform
from drench_sdk.taxonomy import Taxonomy

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.addTransform(
        BatchTransform(
            name='example-batch-flow',
            in_taxonomy=Taxonomy(id=int, name=str),
            out_taxonomy=Taxonomy(name=str),
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
            in_taxonomy=Taxonomy(name=str),
            out_taxonomy=Taxonomy(name=str),
            Jobname='example-job-def',
            AllocatedCapacity=2
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    example_workflow()
