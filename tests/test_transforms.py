'''test transform constructors'''
from drench_sdk import BatchTransform, GlueTransform, QueryTransform

def test_batch_transform():
    '''test batch transform constructor'''
    batch_transform = BatchTransform(
        job_queue='foo',
        job_definition='bar'
    )

    built = batch_transform.states('example-batch-job', 'fail_state', 'canary')

    assert len(built) == 8
    assert built['example-batch-job.run_task'].Resource.endswith(':canary')
    assert batch_transform.job_definition == 'bar'

def test_glue_transform():
    '''test glue transform constructor'''
    glue_transform = GlueTransform(
        job_name='example-job-def',
        allocated_capacity=2,
        report_type='analyze'
    )

    built = glue_transform.states('example-glue-job', 'fail_state', 'canary')

    assert len(built) == 10
    assert glue_transform.allocated_capacity == 2

def test_query_transform():
    '''test query transform constructor'''
    query_transform = QueryTransform(
        query_string='foo',
        database='bar'
    )

    built = query_transform.states('example-query-job', 'fail_state', 'canary')

    assert len(built) == 8
    assert query_transform.database == 'bar'
