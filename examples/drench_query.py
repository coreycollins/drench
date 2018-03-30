"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import QueryTransform
from drench_sdk.taxonomy import Taxonomy

def main():
    """main func"""

    workflow = WorkFlow()

    workflow.addTransform(
        QueryTransform(
            name='test_athena_query',
            in_taxonomy=Taxonomy(name=str),
            out_taxonomy=Taxonomy(name=str),
            QueryString='SELECT companyname, naics FROM us_business LIMIT 100;',
            QueryExecutionContext={'Database':'analytics'},
            ResultConfiguration={'OutputLocation': 's3://temp.compass.com/test_query_results'},
            start=True
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    main()
