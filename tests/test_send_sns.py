#pylint:disable=missing-docstring
from lambdas.send_sns import handler


def test_add_result():
    event = {
        'job_id': 1234,
        'sns': {
            'topic_arn': 'some:long:arn',
            'message': 'err log or json',
            'subject': 'test sns subj'
        }
    }

    handler(event, {})
