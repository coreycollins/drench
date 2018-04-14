#pylint:disable=missing-docstring
from lambdas.add_result import handler


def test_add_result():
    event = {
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
            'name': 'test-query',
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'content_type': 'text',
            'report_url': None,
            'status': 'pass'
        }
    }

    handler(event, {})

def test_add_result_report():
    event = {
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
            'name': 'test-query',
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'content_type': 'text',
            'report_url': None,
            'status': 'pass'
        }
    }

    handler(event, {})
