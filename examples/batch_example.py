from __future__ import print_function
import sys, os
import pkg_resources

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.flows import BatchFlow
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
    'check_batch' : pkg_resources.resource_filename('statemachine', 'lambda/check_batch.py')
}
flow = BatchFlow(
    Name='test',
    OnSucceed='finish',
    OnFail='failed',
    Resources=resources,
    JobQueue='test-queue',
    JobDefinition='sap-job-execution',
    Parameters={
        'job': '$.params.job'
    }
)
input_test.Next = flow.start()

machine = StateMachine()

machine.addState(Name='in', State=input_test, Start=True)
machine.addFlow(flow)
machine.addState(Name='finish', State=SucceedState())
machine.addState(Name='failed', State=FailState())

print(machine.toJson())
