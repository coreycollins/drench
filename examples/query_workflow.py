"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import QueryTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow(sdk_version='test')

    workflow.add_state(
        name='example-query-transform',
        state=QueryTransform(
            database='default',
            query_string='SELECT * FROM "names2" limit 10;',
        )
    )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
