"""example/test script for developing drench_sdk"""
from resources import Resources
from workflow import WorkFlow
from flows import BatchFlow, GlueFlow
from taxonomy import Taxonomy

def main():
    """main func"""
    resources = Resources()

    workflow = WorkFlow(topic_arn=resources.get_arn('sns', 'example-drench-workflow'))

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
            on_succeed='example-glue-job',
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
