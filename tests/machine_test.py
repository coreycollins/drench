from __future__ import print_function
import pytest

from statemachine.machine import Machine
from statemachine.states.batch import BatchState

@pytest.fixture
def machine():
    sm = Machine(setup={'Test':'Test'})
    yield sm

def test_consturct_without_df(machine):
    assert True == True

def test_json_batch_state():
    state = BatchState(
            Resource='arn',
            JobQueue='test-queue',
            JobDefinition='test',
            Parameters={
                'job': 'test'
            },
            End=True
        )
    print(state.toJson())
