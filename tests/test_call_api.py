#pylint:disable=missing-docstring
from lambdas.call_api import handler


def test_check_query():
    event = {
        'job_id': 1234,
        'principal_id': 4321,
        'api_version': 'v1',
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
            'out_path': 's3://com.drench.results/1234/test-query/out',
            'report_url': 's3://foo/bar/out.html'
        },
        'api_call': {
            'path':'/jobs/$.job_id/steps',
            'body':{
                'step':{
                    'name': '$.next.name',
                    'out_path': '$.next.out_path',
                    'content_type': '$.next.content_type',
                    'status': '$.result.status',
                    'report_url': '$.result.report_url'
                }
            },
            'method': 'PUT'
            }
    }

    step_id = handler(event, {})
    assert step_id == 'step_id'
