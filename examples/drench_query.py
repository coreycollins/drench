"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import QueryTransform
from drench_sdk.taxonomy import Taxonomy

def example_workflow():
    """main func"""
    workflow = WorkFlow(pool_id=1234)

    workflow.addTransform(
        QueryTransform(
            name='example-query-transform',
            output_data={
                'path':'s3://temp.compass.com/testing/',
                'taxonomy':Taxonomy(id=int, name=str),
                },
            database='analytics',
            QueryString='SELECT companyname, naics FROM us_business LIMIT 100;',
            Start=True
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    example_workflow()
