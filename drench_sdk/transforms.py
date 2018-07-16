'''flows are fucntion-like packages of states'''
from drench_sdk.utils import get_arn
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self._default_steps = [
            'run_task',
            'wait',
            'check_task',
            'check_choice',
            'finish_choice'
        ]

    def setup(self, name): #pylint:disable=R0201
        '''build $.next'''
        setup = {
            'name': name
        }

        return setup

    def states(self, name, on_fail):
        '''compile and return all steps in the transform'''
        from drench_sdk.config import SDK_VERSION
        steps = {}

        step_names = {step_name: f'{name}.{step_name}' for step_name in self._default_steps}

        steps[name] = PassState(
            Result=self.setup(name),
            ResultPath='$.next',
            Next=step_names['run_task']
        )

        steps[step_names['run_task']] = TaskState(
            Resource=get_arn('lambda', f'function:{SDK_VERSION}-drench-sdk-run-task'),
            Next=step_names['wait'],
            ResultPath='$',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }],
            Catch=[
                {
                    "ErrorEquals": ["States.ALL"],
                    "ResultPath": "$.result.status",
                    "Next": on_fail
                }
            ]

        )

        steps[step_names['wait']] = WaitState(
            Seconds=60,
            Next=step_names['check_task'],
        )


        steps[step_names['check_task']] = TaskState(
            Resource=get_arn('lambda', f'function:{SDK_VERSION}-drench-sdk-check-task'),
            Next=step_names['check_choice'],
            ResultPath=f'$.result.status',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }],
            Catch=[
                {
                    "ErrorEquals": ["States.ALL"],
                    "ResultPath": "$.result.status",
                    "Next": on_fail
                }
            ]
        )

        steps[step_names['check_choice']] = ChoiceState(
            Choices=[
                {
                    'Or': [
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'fail',
                        },
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'pass',
                        }
                    ],
                    'Next': step_names['finish_choice'] #pylint:disable=line-too-long
                }
            ],
            Default=step_names['wait'],
        )

        steps[step_names['finish_choice']] = ChoiceState(
            Choices=[
                {
                    'Variable': f'$.result.status',
                    'StringEquals': 'pass',
                    'Next': self.Next
                }
            ],
            Default=on_fail
            )

        return steps

class LambdaTransform(Transform):
    '''docstring for .'''
    def __init__(self, resource_arn, parameters=None, **kwargs):
        super(LambdaTransform, self).__init__(**kwargs)
        self.resource_arn = resource_arn
        self.parameters = parameters

    def setup(self, name):
        setup = super(LambdaTransform, self).setup(name)
        setup['params'] = self.parameters
        return setup

    def states(self, name, on_fail):
        '''compile and return all steps in the transform'''
        steps = {}

        steps[name] = PassState(
            Result=self.setup(name),
            ResultPath='$.next',
            Next=f'{name}.run'
        )

        steps[f'{name}.run'] = TaskState(
            Resource=self.resource_arn,
            Next=self.Next,
            ResultPath='$',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }],
            Catch=[
                {
                    "ErrorEquals": ["States.ALL"],
                    "ResultPath": "$.result.status",
                    "Next": on_fail
                }
            ]

        )

        return steps

class BatchTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchTransform, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters

    def setup(self, name):
        setup = super(BatchTransform, self).setup(name)
        setup['type'] = 'batch'
        setup['params'] = {
            'jobName': name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition,
            'parameters': {}
        }

        if self.parameters:
            setup['params']['parameters'] = {**setup['params']['parameters'], **self.parameters}

        return setup

class GlueTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_name, arguments=None, allocated_capacity=1, **kwargs):
        super(GlueTransform, self).__init__(**kwargs)
        self.job_name = job_name
        self.arguments = arguments
        self.allocated_capacity = allocated_capacity

    def setup(self, name):
        setup = super(GlueTransform, self).setup(name)
        setup['type'] = 'glue'
        setup['params'] = {
            'JobName': self.job_name,
            'AllocatedCapacity': self.allocated_capacity,
            'Arguments': {}
        }

        if self.arguments:
            setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.arguments}

        return setup


class QueryTransform(Transform):
    '''docstring for .'''
    def __init__(self, query_string, database, out_path, **kwargs):
        super(QueryTransform, self).__init__(**kwargs)
        self.query_string = query_string
        self.database = database
        self.out_path = out_path

    def setup(self, name):
        setup = super(QueryTransform, self).setup(name)
        setup['type'] = 'query'
        setup['params'] = {
            'QueryString': self.query_string,
            'QueryExecutionContext': {
                'Database': self.database
            },
            'ResultConfiguration': {
                'OutputLocation': self.out_path
            }
        }

        return setup
