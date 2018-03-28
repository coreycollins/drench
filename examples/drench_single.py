"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.flows import GlueFlow
from drench_sdk.taxonomy import Taxonomy

def main():
    """main func"""

    workflow = WorkFlow()

    workflow.addFlow(
        GlueFlow(
            name='test_csv_to_orc_sdk',
            in_taxonomy=Taxonomy(name=str),
            out_taxonomy=Taxonomy(name=str),
            Jobname='test_csv_to_orc',
            Arguments={
                'input_path': 's3://temp.compass.com/input.csv',
                'output_path': 's3://temp.compass.com/sdk_test_orc'
                },
            AllocatedCapacity=2,
            start=True
        )
    )

    print(workflow.toJson())

if __name__ == '__main__':
    main()
