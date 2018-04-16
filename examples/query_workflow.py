"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import QueryTransform

def example_workflow():
    """main func"""
    workflow = WorkFlow()

    workflow.add_transform(
        QueryTransform(
            name='example-query-transform',
            database='drench_pools_development',
            query_string='SELECT company, phone FROM "32c87cfee1cd4980ba0a08816f4cc38a" LIMIT 100;',
        )
    )

    print(workflow.to_json())

if __name__ == '__main__':
    example_workflow()
