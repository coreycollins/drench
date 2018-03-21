from workflow import WorkFlow
from flows import BatchFlow, GlueFlow
from taxonomy import Taxonomy
from resource import Resource


workflow = WorkFlow()
resource = Resource()


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
        on_succeed='SuccessSend',
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
