'''flows are fucntion-like packages of states'''
from drench_resources import get_arn
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self,
                 name,
                 report_url=None,
                 content_type='application/text',
                 **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name
        self.report_url = report_url
        self.content_type = content_type

        # defaults to be over-ridden
        self._wait_seconds = 0
        self._on_fail = None

    def setup(self):
        '''build $.next'''
        setup = {
            'name': self.name,
            'content_type': self.content_type,
            'report_url': self.report_url
        }
        return setup

    def states(self):
        '''compile and return all steps in the transform'''
        steps = {}

        steps[f'{self.name}'] = PassState(
            Result=self.setup(),
            ResultPath='$.next',
            Next=f'{self.name}.2.run'
        )

        steps[f'{self.name}.2.run'] = TaskState(
            Resource=get_arn('lambda', 'function:drench-sdk-run-task'),
            Next=f'{self.name}.3.wait',
            ResultPath='$'
        )

        steps[f'{self.name}.3.wait'] = WaitState(
            Seconds=self._wait_seconds,
            Next=f'{self.name}.4.check',
        )


        steps[f'{self.name}.4.check'] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-check-task'),
            Next=f'{self.name}.5.choice',
            ResultPath=f'$.result',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }]
        )

        steps[f'{self.name}.5.choice'] = ChoiceState(
            Choices=[
                {
                    'OR': [
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'fail',
                        },
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'pass',
                        }
                    ],

                    'Next': f'{self.name}.6.add_result'
                }
            ],
            Default=f'{self.name}.3.wait'
        )

        steps[f'{self.name}.6.add_result'] = TaskState(
            Resource=get_arn('lambda', 'function:drench-sdk-add-result'),
            Next=f'{self.name}.7.choice',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }]
        )
        steps[f'{self.name}.7.choice'] = ChoiceState(
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

    def setup(self):
        setup = super(BatchTransform, self).setup()
        setup['type'] = 'glue'
        setup['params'] = {
            'jobname': self.name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition,
            'parameters': {
                '--in_path':'$.next.in_path',
                '--out_path':'$.next.out_path'
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

    def setup(self):
        setup = super(GlueTransform, self).setup()
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

    def setup(self):
        setup = super(QueryTransform, self).setup()
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
