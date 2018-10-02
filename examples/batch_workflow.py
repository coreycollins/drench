#!/usr/bin/env python
'''example/test script for developing drench_sdk'''
from drench_sdk import WorkFlow, AsyncTransform

workflow = WorkFlow()

workflow.add_state(
    name='example-batch-workflow',
    start=True,
    state=AsyncTransform(
        task_type='batch',
        params={
            'jobName': 'example-batch-workflow',
            'jobDefinition': 'canary-scriptrunner',
            'jobQueue': 'core-test-queue-production',
            'parameters': {
                'script': 's3://temp.compass.com/test.py',
                'args': 'hello'
            }
        }
    )
)


if __name__ == '__main__':
    workflow.run({
        'input_file': 'test.txt'
    })
