#pylint:disable=missing-docstring
from lambdas.sdk_util import build_path, find_subs

def test_build_path():
    path = '/jobs/$.job_id/state/$.result.status'
    event = {
        'job_id': '1234',
        'result':{
            'status':'pass'
        },
        'foo': 'bar'
    }

    assert build_path(path, event) == '/jobs/1234/state/pass'

def test_find_subs():
    event = {
        'next':{
            'name': 'foo',
            'out_path': 's3://foo/bar/out',
            'content_type': 'text',
        },
        'result':{
            'status':'pass'
        },
        'foo': 'bar',
        'api_call': {
            'body': {
                'name': '$.next.name',
                'out_path': '$.next.out_path',
                'content_type': '$.next.content_type',
                'status': '$.result.status'
                }
        }
    }

    found = find_subs(event['api_call']['body'], event)
    assert found['name'] == 'foo'
    assert found['out_path'] == 's3://foo/bar/out'
    assert found['content_type'] == 'text'
    assert found['status'] == 'pass'
