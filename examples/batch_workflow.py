'''example/test script for developing drench_sdk'''
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform

def example_workflow():
    '''main func'''
    workflow = WorkFlow()

    workflow.add_state(
        name='example-batch-workflow',
        state=BatchTransform(
            job_definition='sap-job-execution',
            job_queue='production_low',
            parameters={
                'job': 's3://temp.compass.com/test_drench_sap_batch/test_sap_job.atl',
                'job_name': 'test_batch_job'
                }
            )
        )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
