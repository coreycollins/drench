#pylint:disable=missing-docstring
from lambdas.check_task import handler


def test_check_query():
    event = {
        'job_id': 1234,
        'account_id': 4321,
        'next': {
            'in_path': 'some/path',
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'content_type': 'text',
            'report_url': None,
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
            },
        },
        'result': {
            'job_id': '123',
            'out_path': 's3://com.drench.results/1234/test-query/out'
        }
    }

    correct_result = {
        'name': 'test-query',
        'out_path': 's3://com.drench.results/1234/test-query/out',
        'content_type': 'text',
        'report_url': None,
        'status': 'pass',
        'job_id': '123'
    }

    res = handler(event, {})
    assert res == correct_result

def test_run_batch():
    event = {
        'job_id': 2345,
        'account_id': 5432,
        'next': {
            'in_path': 'some/path',
            'out_path': 's3://com.drench.results/1234/test-batch/out',
            'content_type': 'text',
            'report_url': None,
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
            'job_id': '234',
            'out_path': 's3://com.drench.results/1234/test-batch/out'
        }
    }

    correct_result = {
        'name': 'test-batch',
        'out_path': 's3://com.drench.results/1234/test-batch/out',
        'content_type': 'text',
        'report_url': None,
        'status': 'pass',
        'job_id': '234'
    }

    res = handler(event, {})
    assert res == correct_result

def test_run_glue():
    event = {
        'job_id': 3456,
        'account_id': 6543,
        'next': {
            'in_path': 'some/path',
            'out_path': 's3://com.drench.results/1234/test-glue/out',
            'content_type': 'text',
            'report_url': None,
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
            'job_id': '345',
            'out_path': 's3://com.drench.results/1234/test-glue/out'
        }
    }

    correct_result = {
        'name': 'test-glue',
        'out_path': 's3://com.drench.results/1234/test-glue/out',
        'content_type': 'text',
        'report_url': None,
        'status': 'pass',
        'job_id': '345'
    }

    res = handler(event, {})
    assert res == correct_result
