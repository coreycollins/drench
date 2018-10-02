'''flows are fucntion-like packages of states'''
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

def _add_alias(arn, rpc):
    return '{}:{}'.format(arn, rpc)

class AsyncTransform(State):
    '''docstring for Transform.'''
    def __init__(self, task_type, params=None, **kwargs):
        super(AsyncTransform, self).__init__(Type='meta', **kwargs)
        self.task_type = task_type
        self.params = params

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
            'name': name,
            'params': self.params,
            'type': self.task_type
        }

        return setup

    def states(self, name, call_function, on_fail):
        '''compile and return all steps in the transform'''
        steps = {}

        step_names = {step_name: f'{name}.{step_name}' for step_name in self._default_steps}

        steps[name] = PassState(
            Result=self.setup(name),
            ResultPath='$.next',
            Next=step_names['run_task']
        )

        steps[step_names['run_task']] = TaskState(
            Resource=_add_alias(call_function, 'run_task'),
            Next=step_names['wait'],
            ResultPath='$.result.identifiers',
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
            Resource=_add_alias(call_function, 'check_task'),
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

class Transform(State):
    '''docstring for .'''
    def __init__(self, resource_arn, params=None, **kwargs):
        super(Transform, self).__init__(**kwargs)
        self.resource_arn = resource_arn
        self.params = params

    def setup(self, name):
        '''build $.next'''
        setup = {
            'name': name,
            'params': self.params
        }

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
            Next=f'{name}.cleanup',
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

        steps[f'{name}.cleanup'] = PassState(
            Result='pass',
            ResultPath='$.result.status',
            Next=self.Next
        )

        return steps

# class BatchTransform(Transform):
#     '''docstring for .'''
#     def __init__(self, job_queue, job_definition, parameters=None, container_overrides=None, **kwargs):
#         super(BatchTransform, self).__init__(**kwargs)
#         self.job_queue = job_queue
#         self.job_definition = job_definition
#         self.parameters = parameters
#         self.container_overrides = container_overrides
#
#     def setup(self, name):
#         setup = super(BatchTransform, self).setup(name)
#         setup['type'] = 'batch'
#         setup['params'] = {
#             'jobName': name,
#             'jobQueue':self.job_queue,
#             'jobDefinition': self.job_definition,
#             'parameters': {},
#             'containerOverrides': {}
#         }
#
#         if self.parameters:
#             setup['params']['parameters'] = {**setup['params']['parameters'], **self.parameters}
#
#         if self.container_overrides:
#             setup['params']['containerOverrides'] = {**setup['params']['containerOverrides'], **self.container_overrides}
#
#
#         return setup
#
# class GlueTransform(Transform):
#     '''docstring for .'''
#     def __init__(self, job_name, arguments=None, allocated_capacity=1, **kwargs):
#         super(GlueTransform, self).__init__(**kwargs)
#         self.job_name = job_name
#         self.arguments = arguments
#         self.allocated_capacity = allocated_capacity
#
#     def setup(self, name):
#         setup = super(GlueTransform, self).setup(name)
#         setup['type'] = 'glue'
#         setup['params'] = {
#             'JobName': self.job_name,
#             'AllocatedCapacity': self.allocated_capacity,
#             'Arguments': {}
#         }
#
#         if self.arguments:
#             setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.arguments}
#
#         return setup
