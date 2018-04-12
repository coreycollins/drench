'''flows are fucntion-like packages of states'''
from drench_sdk.resources import Resources
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self, name, run_next=None, report=False, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name
        self.report = report

        self.resources = Resources()

        # defaults to be over-ridden
        self.wait_seconds = 0
        self.on_fail = None
        self.run_next = run_next

        self.steps = {}

    def setup(self):
        '''build $.next'''
        setup = {
            'name': self.name,
            'report': self.report,
            'account_id': self.resources.get_account()
        }
        return setup

    def states(self):
        '''compile and return all steps in the transform'''
        self.steps = {}

        self.steps[f'{self.name}'] = PassState(
            Result=self.setup(),
            ResultPath='$.next',
            Next=f'{self.name}.2.run'
        )

        self.steps[f'{self.name}.2.run'] = TaskState(
            Resource=self.resources.get_arn('lambda', 'function:development-run_task'),
            Next=f'{self.name}.3.wait',
            ResultPath='$'
        )

        self.steps[f'{self.name}.3.wait'] = WaitState(
            Seconds=self.wait_seconds,
            Next=f'{self.name}.4.check',
        )


        self.steps[f'{self.name}.4.check'] = TaskState(
            Resource=self.resources.get_arn('lambda', f'function:development-check_task'),
            Next=f'{self.name}.5.choice',
            ResultPath=f'$.result',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }]
        )

        self.steps[f'{self.name}.5.choice'] = ChoiceState(
            Choices=[
                {
                    'OR': [
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'FAILED',
                        },
                        {
                            'Variable': f'$.result.status',
                            'StringEquals': 'SUCCEEDED',
                        }
                    ],

                    'Next': f'{self.name}.6.add_result'
                }
            ],
            Default=f'{self.name}.{len(self.steps)-1}.wait'
        )

        self.steps[f'{self.name}.6.add_result'] = TaskState(
            Resource=self.resources.get_arn('lambda', 'function:development-add_result'),
            Next=f'{self.name}.7.choice',
            ResultPath='$.add_result.status',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }]
        )
        self.steps[f'{self.name}.7.choice'] = ChoiceState(
            Choices=[
                {
                    'Variable': f'$.result.status',
                    'StringEquals': 'SUCCEEDED',
                    'Next': self.run_next
                }
            ],
            Default=self.on_fail
            )

        return self.steps

class BatchTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchTransform, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters
        self.wait_seconds = 300

    def setup(self):
        setup = super(BatchTransform, self).setup()
        setup['type'] = 'glue'
        setup['params'] = {
            'jobname': self.name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition
        }

        setup['params']['parameters'] = {
            '--in_path':'$.next.in_path',
            '--out_path':'$.next.out_path'
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
        self.wait_seconds = 600

    def setup(self):
        setup = super(GlueTransform, self).setup()
        setup['type'] = 'glue'
        setup['params'] = {
            'JobName': self.job_name,
            'AllocatedCapacity': self.allocated_capacity
        }

        setup['params']['arguments'] = {
            '--in_path':'$.next.in_path',
            '--out_path':'$.next.out_path'
        }

        if self.arguments:
            setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.arguments}

        return setup


class QueryTransform(Transform):
    '''docstring for .'''
    def __init__(self, query_string, database, **kwargs):
        super(QueryTransform, self).__init__(**kwargs)
        self.query_string = query_string
        self.query_execution_context = {'Database': database}
        self.result_configuration = {'OutputLocation': '$.next.out_path'}
        self.wait_seconds = 30

    def setup(self):
        setup = super(QueryTransform, self).setup()
        setup['type'] = 'query'
        setup['params'] = {
            'QueryString': self.query_string,
            'QueryExecutionContext': self.query_execution_context,
            'ResultConfiguration': self.result_configuration
        }

        return setup
