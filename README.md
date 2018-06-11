# Drench SDK

A set of tools for automating business logic on the Drench API.

Documentation:

## Quickstart Guide

Install the sdk like so...

```
pip install drench_sdk
```

Create a workflow script called `example.py`:

```python
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform

def main():
    '''main func'''
    workflow = WorkFlow()

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
```

Test the workflow script...

```
drench_sdk run example.py
```

Create a Sink on the Drench API...

```
drench_sdk sink put --name "Example Sink" example.py
```
