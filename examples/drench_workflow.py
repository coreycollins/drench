"""example/test script for developing drench_sdk"""
from drench_sdk.workflow import WorkFlow
from drench_sdk.transforms import BatchTransform, GlueTransform, QueryTransform
from drench_sdk.states import TaskState

def main():
    """main func"""
    workflow = WorkFlow()

    workflow.add_state(
        name='example-query-transform',
        state=QueryTransform(
            database='some_db',
            query_string='SELECT id, name FROM some_table LIMIT 100;',
            Next='example-batch-transform',
            Start=True
        )
    )

    workflow.add_state(
        name='example-batch-transform',
        state=BatchTransform(
            job_queue='test-queue',
            job_definition='sap-job-execution',
            parameters={
                '--flag': 'some-value'
            },
            Next='example-task',
        )
    )

    workflow.add_state(
        name='example-task',
        state=TaskState(
            Next='example-glue-transform',
            Resource='function:drench-function',
            ResultPath='$',
        )
    )

    workflow.add_state(
        name='example-glue-transform',
        state=GlueTransform(
            job_name='example-job-def',
            allocated_capacity=2,
            arguments={
                '--command-line-switch': True
            }
        )
    )

    return workflow

if __name__ == '__main__':
    main()
