'''test transform constructors'''
from drench_sdk import BatchTransform, GlueTransform, QueryTransform

def test_batch_transform():
    '''test batch transform constructor'''
    batch_transform = BatchTransform(
        job_queue='foo',
        job_definition='bar'
    )

    built = batch_transform.states('example-batch-job', 'canary')

    assert len(built) == 7
    assert built['example-batch-job.2.run'].Resource.endswith(':canary')
    assert batch_transform.job_definition == 'bar'

def test_glue_transform():
    '''test glue transform constructor'''
    glue_transform = GlueTransform(
        job_name='example-job-def',
        allocated_capacity=2
    )

    built = glue_transform.states('example-glue-job', 'canary')

    assert len(built) == 7
    assert built['example-glue-job.2.run'].Resource.endswith(':canary')
    assert glue_transform.allocated_capacity == 2

def test_query_transform():
    '''test query transform constructor'''
    query_transform = QueryTransform(
        query_string='foo',
        database='bar'
    )

    built = query_transform.states('example-query-job', 'canary')

    assert len(built) == 7
    assert built['example-query-job.2.run'].Resource.endswith(':canary')
    assert query_transform.database == 'bar'
