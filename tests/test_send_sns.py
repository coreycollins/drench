#pylint:disable=missing-docstring
from lambdas.send_sns import handler


def test_add_result():
    event = {
        'job_id': 1234,
        'err_info': 'err log or json',
        'sns': {
            'topic_arn': 'some:long:arn',
            'subject': 'test sns subj'
        }
    }

    handler(event, {})
