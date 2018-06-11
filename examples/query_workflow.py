"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import QueryTransform

def main():
    """main func"""
    workflow = WorkFlow()

    workflow.add_state(
        name='example-query-transform',
        state=QueryTransform(
            database='default',
            query_string='SELECT * FROM "names2" limit 10;',
        )
    )

    return workflow

if __name__ == '__main__':
    main()
