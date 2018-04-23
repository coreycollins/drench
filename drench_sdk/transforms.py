'''flows are fucntion-like packages of states'''
from drench_resources import get_arn
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self,
                 report_url=None,
                 content_type='application/text',
                 **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.report_url = report_url
        self.content_type = content_type

        # defaults to be over-ridden
        self._wait_seconds = 0
        self._on_fail = None

    def setup(self, name):
        '''build $.next'''
        setup = {
            'name': name,
            'content_type': self.content_type,
            'report_url': self.report_url
        }

        return setup

    def states(self, name, lambda_version):
        '''compile and return all steps in the transform'''
        steps = {}

        steps[f'{name}'] = PassState(
            Result=self.setup(name),
            ResultPath='$.next',
            Next=f'{name}.2.run'
        )

        steps[f'{name}.2.run'] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-run-task:{lambda_version}'),
            Next=f'{name}.3.wait',
            ResultPath='$',
            Catch=[
                {
                    "ErrorEquals": ["States.ALL"],
                    "ResultPath": "$.result.status",
                    "Next": self._on_fail
                }
            ]

        )

        steps[f'{name}.3.wait'] = WaitState(
            Seconds=self._wait_seconds,
            Next=f'{name}.4.check',
        )


        steps[f'{name}.4.check'] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-check-task:{lambda_version}'),
            Next=f'{name}.5.choice',
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
                    "Next": self._on_fail
                }
            ]
        )

        steps[f'{name}.5.choice'] = ChoiceState(
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

                    'Next': f'{name}.6.add_result'
                }
            ],
            Default=f'{name}.3.wait'
        )

        steps[f'{name}.6.add_result'] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-add-result:{lambda_version}'),
            Next=f'{name}.7.choice',
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
                    "Next": self._on_fail
                }
            ]
        )
        steps[f'{name}.7.choice'] = ChoiceState(
            Choices=[
                {
                    'Variable': f'$.result.status',
                    'StringEquals': 'pass',
                    'Next': self.Next
                }
            ],
            Default=self._on_fail
            )

        return steps

class BatchTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchTransform, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters
        self._wait_seconds = 60

    def setup(self, name):
        setup = super(BatchTransform, self).setup(name)
        setup['type'] = 'batch'
        setup['params'] = {
            'jobName': name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition,
            'parameters': {
                'in_path':'$.next.in_path',
                'out_path':'$.next.out_path'
            }
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
        self._wait_seconds = 60

    def setup(self, name):
        setup = super(GlueTransform, self).setup(name)
        setup['type'] = 'glue'
        setup['params'] = {
            'JobName': self.job_name,
            'AllocatedCapacity': self.allocated_capacity,
            'Arguments': {
                '--in_path':'$.next.in_path',
                '--out_path':'$.next.out_path'
            }
        }

        if self.arguments:
            setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.arguments}

        return setup


class QueryTransform(Transform):
    '''docstring for .'''
    def __init__(self, query_string, database, **kwargs):
        super(QueryTransform, self).__init__(**kwargs)
        self.query_string = query_string
        self.database = database
        self._wait_seconds = 30

    def setup(self, name):
        setup = super(QueryTransform, self).setup(name)
        setup['type'] = 'query'
        setup['params'] = {
            'QueryString': self.query_string,
            'QueryExecutionContext': {
                'Database': self.database
            },
            'ResultConfiguration': {
                'OutputLocation': '$.next.out_path'
            }
        }

        return setup
