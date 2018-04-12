import pytest

from lambdas.run_task import handler

def test_no_job_id():
    with pytest.raises(KeyError):
        handler({}, {})

def test_no_account_id():
    event = {
        'job_id': 1234,
        'next': {
            'in_path': 'some/path'
        }
    }

    with pytest.raises(KeyError) as error:
        handler(event, {})

    assert str(error.value) == "'account_id'"

def test_run_task():
    event = {
        'job_id': 1234,
        'account_id': 4321,
        'next': {
            'in_path': 'some/path',
            'name': 'test',
            'type': 'query',
            'params': {
                'QueryString': 'SELECT *',
                'ResultConfiguration': {
                    'OutputLocation': '$.next.out_path'
                }
            }
        }
    }
    res = handler(event, {})

    assert res['result']['job_id'] == '123'
