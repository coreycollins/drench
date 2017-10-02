from __future__ import print_function
import sys, os

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.flows import BatchFlow
from statemachine import StateMachine
from statemachine.states import PassState

flow = BatchFlow(
    Name='test',
    OnSucceed='finish',
    OnFail='failed',
    JobQueue='test-queue',
    JobDefinition='sap-job-execution',
    Parameters={
        'job': 'TEST_Boolean'
    }
)

machine = StateMachine()
machine.addFlow(flow, Start=True)
machine.addState(Name='finish', State=PassState(End=True))
machine.addState(Name='failed', State=PassState(End=True))

print(machine.toJson())
