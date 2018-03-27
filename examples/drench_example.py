"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.flows import BatchFlow, GlueFlow
from drench_sdk.taxonomy import Taxonomy

def main():
    """main func"""

    workflow = WorkFlow()

    workflow.addFlow(
        BatchFlow(
            name='example-batch-flow',
            in_taxonomy=Taxonomy(id=int, name=str),
            out_taxonomy=Taxonomy(name=str),
            job_queue='test-queue',
            job_definition='sap-job-execution',
            parameters={
                'job': '$.params.job'
            },
            Next='example-glue-job',
            start=True
        )
    )

    workflow.addFlow(
        GlueFlow(
            name='example-glue-job',
            in_taxonomy=Taxonomy(name=str),
            out_taxonomy=Taxonomy(name=str),
            Jobname='example-job-def',
            AllocatedCapacity=2
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    main()
