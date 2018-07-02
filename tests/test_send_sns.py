#pylint:disable=missing-docstring
from lambdas.send_sns import handler


def test_add_result():
    event = {
        'topic_arn': 'some:long:arn',
        'job_id': 1234
    }

    handler(event, {})
