'''example/test script for developing drench_sdk'''
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform

def example_workflow():
    '''main func'''
    workflow = WorkFlow()

    workflow.add_transform(
        BatchTransform(
            name='example-batch-workflow',
            job_definition='development_nightcrawler',
            job_queue='production_low',
            parameters={
                'email': 'ejaros@cmsdm.com',
                'file': 'Upload/false200.csv',
                'name': 'urgz_test',
                'site': 'test'
                }
            )
        )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
