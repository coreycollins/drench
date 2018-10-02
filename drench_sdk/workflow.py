'''workflows: chained and orchestrated sets of transforms'''
import os
import json
import time
import uuid
import boto3

from drench_sdk.states import  ChoiceState, FailState, PassState, SucceedState, State, TaskState
from drench_sdk.transforms import Transform, AsyncTransform

FAILED = '__failed'
FINISHED = '__finished'
END_SELECTOR = '__end_selector'
STATUS_TRANSLATE = '__status_translate'
STATUS_FINISHED = '__status_finished'
STATUS_FAILED = '__status_failed'

def _sfn_waiter(execution_arn):
    """ Wait for sfn machine to exit """
    client = boto3.client('stepfunctions')
    while True:
        res = client.describe_execution(executionArn=execution_arn)

        if res['status'] == 'SUCCEEDED':
            return res['output']
        elif res['status'] in ['FAILED', 'TIMED_OUT', 'ABORTED']:
            res = client.get_execution_history(
                executionArn=execution_arn,
                maxResults=25
            )
            print(json.dumps(res, indent=4, default=str))
            raise Exception("State machine failed..")

        time.sleep(5)

class WorkFlow(object):
    """Generates a state machine for AWS SNF"""

    def __init__(self, config_file=None, comment=None, timeout=None, version=None):
        self.sfn = {}

        if not config_file:
            config_file = os.path.join(os.curdir, 'drench.json')

        resources = json.load(open(config_file, 'r'))
        self.resource_arn = resources['function_arn']
        self.role_arn = resources['role_arn']

        if comment:
            self.sfn['Comment'] = comment

        if timeout:
            self.sfn['TimeoutSeconds'] = timeout

        if version:
            self.sfn['Version'] = version

        self.sfn['States'] = {
            STATUS_TRANSLATE: ChoiceState(
                Choices=[
                    {
                        'Variable': f'$.result.status',
                        'StringEquals': 'pass',
                        'Next': STATUS_FINISHED
                    }
                ],
                Default=STATUS_FAILED
            ),

            STATUS_FINISHED: PassState(
                Result='finished',
                ResultPath='$.result.status',
                Next=END_SELECTOR
            ),

            STATUS_FAILED: PassState(
                Result='failed',
                ResultPath='$.result.status',
                Next=END_SELECTOR
            ),
            END_SELECTOR: ChoiceState(
                Choices=[
                    {
                        'Variable': '$.result.status',
                        'StringEquals': 'finished',
                        'Next': FINISHED
                    }
                ],
                Default=FAILED
            ),
            FINISHED: SucceedState(),
            FAILED: FailState()
        }

    def add_state(self, name, state, start=False):
        """ adds transform's states to worktransform, overwrites in the case of name colissions"""

        if name in self.sfn['States'].keys():
            raise Exception(f'The transform name {name} is already in use')

        if start:
            self.sfn['StartAt'] = name

        if not state.Next:
            state.Next = STATUS_TRANSLATE

        if isinstance(state, Transform):
            self.sfn['States'] = {
                **self.sfn['States'],
                **state.states(
                    name=name,
                    on_fail=STATUS_TRANSLATE
                )
            }
        elif isinstance(state, AsyncTransform):
            self.sfn['States'] = {
                **self.sfn['States'],
                **state.states(
                    name=name,
                    call_function=self.resource_arn,
                    on_fail=STATUS_TRANSLATE
                )
            }
        elif isinstance(state, TaskState): #users adding TaskStates must know lambda version to call
            if not state.Catch:
                state.Catch = [
                    {
                        "ErrorEquals": ["States.ALL"],
                        "ResultPath": "$.result.status",
                        "Next": STATUS_TRANSLATE
                    }
                ]
            self.sfn['States'][name] = state

    def run(self, params=None):
        """ Run the workflow with a temporary statemachine """
        client = boto3.client('stepfunctions')
        print('Creating state machine...')
        resp = client.create_state_machine(
            name=uuid.uuid4().hex,
            definition=self.to_json(),
            roleArn=self.role_arn
        )
        machine_arn = resp["stateMachineArn"]

        params = params or {}

        try:
            print('Running state machine...')
            resp = client.start_execution(stateMachineArn=machine_arn, input=json.dumps(params))
            _sfn_waiter(resp['executionArn'])
        finally:
            print('Deleting state machine...')
            client.delete_state_machine(stateMachineArn=machine_arn)

    def as_dict(self):
        """ return state machine as a dict """
        def serialize(obj):
            '''coerce objects to dict as necessary'''
            if isinstance(obj, dict):
                return {k: serialize(v.__dict__)
                           if isinstance(v, State) else serialize(v)
                        for (k, v) in obj.items() if v}
            return obj

        if not self.sfn['StartAt']:
            raise Exception('The workflow does not have a start state defined.')

        return serialize(self.sfn)

    def to_json(self):
        """dump Worktransform to AWS Step Function JSON"""
        return json.dumps(self.as_dict(), sort_keys=True)
