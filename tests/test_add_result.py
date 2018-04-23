#pylint:disable=missing-docstring
from lambdas.add_result import handler


def test_add_result():
    event = {
        'api_version': 'v0',
        'job_id': 1234,
        'principal_id': 4321,
        'next': {
            'in_path': 'some/path',
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'content_type': 'text',
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
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'status': 'pass'
        }
    }

    assert handler(event, {}) == event

def test_add_result_report():
    event = {
        'api_version': 'v0',
        'job_id': 1234,
        'principal_id': 4321,
        'next': {
            'in_path': 'some/path',
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'content_type': 'text',
            'report_url': 'http://example.com',
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
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'status': 'pass'
        }
    }

    assert handler(event, {}) == event
