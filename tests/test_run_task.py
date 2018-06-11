#pylint:disable=missing-docstring
import pytest

from lambdas.run_task import handler

def test_run_query():
    event = {
        'job_id': 1234,
        'principal_id': 4321,
        'next': {
            'name': 'test-query',
            'type': 'query',
            'params': {
                'QueryString': 'SELECT *',
                'ResultConfiguration': {
                    'OutputLocation': 's3://drench.io.results/{{$.job_id}}/test-query/out'
                },
                "QueryExecutionContext": {
                    "Database": "foo"
                },
            }
        }
    }
    res = handler(event, {})

    assert res['result']['job_id'] == '123'
    assert res['next']['params']['ResultConfiguration']['OutputLocation'] == 's3://drench.io.results/1234/test-query/out'

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
                'parameters': {}
            }
        },
        'result': {
            'out_path':'some/path'
        }
    }
    res = handler(event, {})
    assert res['result']['job_id'] == '234'

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
                'Arguments': {}
            }
        },
        'result': {
            'out_path':'some/path'
        }
    }
    res = handler(event, {})
    assert res['result']['job_id'] == '345'
