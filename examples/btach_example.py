from __future__ import print_function
import sys, os
import json

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.batch import BatchFlow
from statemachine.machine import Machine
from statemachine.states import PassState

flow = BatchFlow(
        Name='test',
        OnSucceed='finish',
        OnFail='failed',
        JobQueue='test-queue',
        JobDefinition='test',
        Parameters={
            'job': 'test'
        }
    )

machine = Machine()

machine.addFlow(flow)
machine.addState(Name='finish', State=PassState())
machine.addState(Name='failed', State=PassState())

print(machine.toJson())
