"""example/test script for developing drench_sdk"""
import json
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform

def test_workflow():
    """main func"""
    # workflow = WorkFlow(pool_id=1234)
    #
    # workflow.addTransform(
    #     BatchTransform(
    #         name='example-batch-flow',
    #         job_queue='test-queue',
    #         job_definition='sap-job-execution',
    #         parameters={
    #             'job': '$.params.job'
    #         },
    #         Next='example-glue-job',
    #         Start=True
    #     )
    # )
    #
    # workflow.addTransform(
    #     GlueTransform(
    #         name='example-glue-job',
    #         Jobname='example-job-def',
    #         AllocatedCapacity=2
    #     )
    # )
    #
    # correct_sfn = ''
    # with open('tests/correct.json') as file_handle:
    #     correct_sfn = file_handle.read()
    #
    # assert json.loads(workflow.toJson()) == json.loads(correct_sfn)
