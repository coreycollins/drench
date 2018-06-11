'''example/test script for developing drench_sdk'''
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform

def main():
    '''main func'''
    workflow = WorkFlow(sdk_version='canary')

    workflow.add_state(
        name='example-batch-workflow',
        state=BatchTransform(
            job_definition='fetch-and-run',
            job_queue='test',
            parameters={
                'script': 's3://temp.compass.com/test.py',
                'args': 'hello'
            }
        )
    )

    return workflow

if __name__ == '__main__':
    main()
