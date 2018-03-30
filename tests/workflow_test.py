"""example/test script for developing drench_sdk"""
import json
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform
from drench_sdk.taxonomy import Taxonomy

def test_workflow():
    """main func"""
    workflow = WorkFlow()

    workflow.addFlow(
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
            start=True
        )
    )

    workflow.addFlow(
        GlueTransform(
            name='example-glue-job',
            in_taxonomy=Taxonomy(name=str),
            out_taxonomy=Taxonomy(name=str),
            Jobname='example-job-def',
            AllocatedCapacity=2
        )
    )

    correct_sfn = ''
    with open('tests/correct.json') as file_handle:
        correct_sfn = file_handle.read()

    assert json.loads(workflow.toJson()) == json.loads(correct_sfn)
