from __future__ import print_function
import sys, os
import json

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.batch import BatchFlow
from statemachine import StateMachine
from statemachine.states import PassState

machine = StateMachine()
machine.addFlow(BatchFlow(
        Name='test',
        OnSucceed='finish',
        OnFail='failed',
        JobQueue='test-queue',
        JobDefinition='test',
        Parameters={
            'job': 'test'
        }
))
machine.addState(Name='finish', State=PassState())
machine.addState(Name='failed', State=PassState())

print(machine.toJson())
