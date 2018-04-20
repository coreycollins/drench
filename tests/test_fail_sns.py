#pylint:disable=missing-docstring
from lambdas.fail_sns import handler


def test_add_result():
    event = {
        'job_id': 1234,
        'topic_arn': 'some:long:arn',
        'err_info': 'err log or json'
    }

    handler(event, {})
