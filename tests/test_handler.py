''' handler test suite '''
from drench_sdk.handler import main

class MockContext(object):
    ''' mock the AWS context object '''
    def __init__(self, name):
        self.name = name

    @property
    def invoked_function_arn(self):
        ''' return a funtion name '''
        return 'arn:fucntion:drench:{}'.format(self.name)


def test_run_task_rpc():
    ''' should run a task '''
    event = {
        'next': {
            'type': 'batch',
            'params': {
                'jobName': 'foo',
                'jobQueue': 'bar',
                'jobDefinition': 'baz',
                'parameters': {}
            }
        }
    }
    context = MockContext('run_task')
    res = main(event, context)

    assert res['JobId'] == '234'

def test_check_task_rpc():
    ''' should check a task '''
    event = {
        'next': {
            'type': 'batch'
        },
        'result': {
            'identifiers': {
                'JobId': '234'
            }
        }

    }
    context = MockContext('check_task')
    res = main(event, context)

    assert res == 'pass'
