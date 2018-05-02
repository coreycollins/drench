#pylint:disable=missing-docstring
import pytest

from lambdas.run_task import handler


def test_no_in_path():
    event = {
        'next': {
            'type':'batch'
            }
    }

    with pytest.raises(KeyError) as error:
        handler(event, {})

    assert str(error.value) == "'in_path'"

def test_no_in_path_with_query():
    event = {
        'next': {
            'type':'query'
            }
    }

    with pytest.raises(KeyError) as error:
        handler(event, {})

    assert str(error.value) == "'job_id'"


def test_no_job_id():
    event = {
        'next': {
            'in_path': 'some/path',
            'type':'batch'
        }
    }

    with pytest.raises(KeyError) as error:
        handler(event, {})

    assert str(error.value) == "'job_id'"

def test_no_account_id():
    event = {
        'job_id': 1234,
        'next': {
            'in_path': 'some/path',
            'type':'batch'
        }
    }

    with pytest.raises(KeyError) as error:
        handler(event, {})

    assert str(error.value) == "'principal_id'"

def test_run_query():
    event = {
        'job_id': 1234,
        'principal_id': 4321,
        'next': {
            'in_path': 'some/path',
            'name': 'test-query',
            'type': 'query',
            'params': {
                'QueryString': 'SELECT *',
                'ResultConfiguration': {
                    'OutputLocation': '$.next.out_path'
                },
                "QueryExecutionContext": {
                    "Database": "foo"
                },
            }
        }
    }
    res = handler(event, {})

    correct_path = 's3://drench.io.results/1234/test-query/out'
    assert res['result']['job_id'] == '123'
    assert res['next']['params']['ResultConfiguration']['OutputLocation'] == correct_path

def test_run_batch():
    event = {
        'job_id': 2345,
        'principal_id': 5432,
        'next': {
            'name': 'test-batch',
            'type': 'batch',
            'params': {
                'jobName': 'foo',
                'jobQueue': 'bar',
                'jobDefinition': 'baz',
                'parameters': {
                    '--in_path': '$.next.in_path',
                    '--out_path': '$.next.out_path'
                }
            }
        },
        'result': {
            'out_path':'some/path'
        }
    }
    res = handler(event, {})

    correct_in_path = 'some/path'
    correct_out_path = 's3://drench.io.results/2345/test-batch/out'
    assert res['result']['job_id'] == '234'
    assert res['next']['params']['parameters']['--in_path'] == correct_in_path
    assert res['next']['params']['parameters']['--out_path'] == correct_out_path

def test_run_glue():
    event = {
        'job_id': 3456,
        'principal_id': 6543,
        'next': {
            'name': 'test-glue',
            'type': 'glue',
            'params': {
                'JobName': 'foo',
                'AllocatedCapacity': 2,
                'Arguments': {
                    '--in_path': '$.next.in_path',
                    '--out_path': '$.next.out_path'
                }
            }
        },
        'result': {
            'out_path':'some/path'
        }
    }
    res = handler(event, {})

    correct_in_path = 'some/path'
    correct_out_path = 's3://drench.io.results/3456/test-glue/out'
    assert res['result']['job_id'] == '345'
    assert res['next']['params']['Arguments']['--in_path'] == correct_in_path
    assert res['next']['params']['Arguments']['--out_path'] == correct_out_path
