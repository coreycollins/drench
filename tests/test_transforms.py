'''test transform constructors'''
from drench_sdk import BatchTransform, GlueTransform, QueryTransform

def test_batch_transform():
    '''test batch transform constructor'''
    batch_transform = BatchTransform(
        name='example-batch-job',
        job_queue='foo',
        job_definition='bar',
    )

    assert len(batch_transform.states()) == 7
    assert batch_transform.job_definition == 'bar'

def test_glue_transform():
    '''test glue transform constructor'''
    glue_transform = GlueTransform(
        name='example-glue-job',
        job_name='example-job-def',
        allocated_capacity=2
    )

    assert len(glue_transform.states()) == 7
    assert glue_transform.allocated_capacity == 2

def test_query_transform():
    '''test query transform constructor'''
    query_transform = QueryTransform(
        name='example-query-job',
        query_string='foo',
        database='bar'
    )

    assert len(query_transform.states()) == 7
    assert query_transform.database == 'bar'
