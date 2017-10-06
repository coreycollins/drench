from __future__ import print_function
import sys, os
import pkg_resources

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.flows import BatchFlow, SNSFlow
from statemachine import StateMachine
from statemachine.states import PassState, SucceedState, FailState

input_test = PassState(
    Result={
        'params':{
            'job':'TEST_Boolean'
        }
    },
    ResultPath='$'
)

resources = {
    'run_batch' : pkg_resources.resource_filename('statemachine', 'lambda/run_batch.py'),
    'check_batch' : pkg_resources.resource_filename('statemachine', 'lambda/check_batch.py'),
    'send_sns' : pkg_resources.resource_filename('statemachine', 'lambda/send_sns.py')
}
batch_flow = BatchFlow(
    Name='test',
    OnSucceed='SuccessSend',
    OnFail='failed',
    Resources=resources,
    JobQueue='test-queue',
    JobDefinition='sap-job-execution',
    Parameters={
        'job': '$.params.job'
    }
)
input_test.Next = batch_flow.start()

sns_flow = SNSFlow(
    Name='SuccessSend',
    OnSucceed='finish',
    OnFail='failed',
    Resources=resources,
    TopicArn='sns:example:topic',
    Subject='Job succeeded.'
    Message='Job succeeded.'
)

machine = StateMachine()

machine.addState(Name='in', State=input_test, Start=True)
machine.addFlow(batch_flow)
machine.addFlow(sns_flow)
machine.addState(Name='finish', State=SucceedState())
machine.addState(Name='failed', State=FailState())

print(machine.toJson())
