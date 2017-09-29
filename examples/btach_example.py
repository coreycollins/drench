from __future__ import print_function
import sys, os
import json

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
from statemachine.batch import BatchFlow

def encode_complex(obj):
    return dict((k, v) for k, v in obj.__dict__.iteritems() if v)

    return json.dumps(self, default=encode_complex)

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

j = json.dumps(flow.states(), default=encode_complex, indent=4, sort_keys=True)
print(j)
