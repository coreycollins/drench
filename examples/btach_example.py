from __future__ import print_function
import sys, os
import json

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.batch import BatchFlow

flow = BatchFlow(
        Name='test',
        OnSucceed='suc',
        OnFail='fail',
        JobQueue='test-queue',
        JobDefinition='test',
        Parameters={
            'job': 'test'
        }
    )

for state in flow.states():
    print(state.toJson())
