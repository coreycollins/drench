from __future__ import print_function
import sys, os
import pkg_resources

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.flows import GlueFlow, SNSFlow
from statemachine import StateMachine
from statemachine.states import PassState, SucceedState, FailState

resources = {
    'run_glue' : pkg_resources.resource_filename('statemachine', 'lambda/run_glue.py'),
    'check_glue' : pkg_resources.resource_filename('statemachine', 'lambda/check_glue.py'),
    'send_sns' : pkg_resources.resource_filename('statemachine', 'lambda/send_sns.py')
}

machine = StateMachine()

machine.addState(
    Name='in',
    State=PassState(
        Next='test',
        Result={
            'process_id':'123',
            'subs': {
                'deps': {
                    'test_glue':'s3://com.compass.artifacts/123/us-consumer/src/glue/test.py'
                },
                'remotepath':'s3://com.compass.artifacts/123/out/'
            }
        },
        ResultPath='$'
    ),
    Start=True
)
machine.addFlow(
    GlueFlow(
        Name='test',
        OnSucceed='SuccessSend',
        OnFail='failed',
        Resources=resources,
        JobName='dev-glue-job',
        Arguments={
            'scriptLocation':'$.subs.deps.test_glue',
            'remotepath':'$.subs.remotepath',
            'files':'input.txt'
        }
    )
)
machine.addFlow(
    SNSFlow(
        Name='SuccessSend',
        OnSucceed='finish',
        OnFail='failed',
        Resources=resources,
        TopicArn='sns:example:topic',
        Subject='Job succeeded.',
        Message='Job succeeded.'
    )
)
machine.addState(Name='finish', State=SucceedState())
machine.addState(Name='failed', State=FailState())

print(machine.toJson())
