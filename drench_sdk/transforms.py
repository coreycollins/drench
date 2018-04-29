'''flows are fucntion-like packages of states'''
from drench_sdk.utils import get_arn
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self,
                 report_type=None,
                 content_type='application/text',
                 **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.report_type = report_type
        self.content_type = content_type
        self._default_steps = [
            'run_task',
            'wait',
            'check_task',
            'check_choice',
            'build_generate_report',
            'generate_report',
            'build_add_result',
            'add_result',
            'finish_choice'
        ]

    def setup(self, name):
        '''build $.next'''
        setup = {
            'name': name,
            'content_type': self.content_type,
            'report_type': self.report_type
        }

        return setup

    def states(self, name, on_fail, sdk_version):
        '''compile and return all steps in the transform'''
        steps = {}

        step_names = {step_name: f'{name}.{step_name}' for step_name in self._default_steps}

        steps[name] = PassState(
            Result=self.setup(name),
            ResultPath='$.next',
            Next=step_names['run_task']
        )

        steps[step_names['run_task']] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-run-task:{sdk_version}'),
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
            Resource=get_arn('lambda', f'function:drench-sdk-check-task:{sdk_version}'),
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
                    'Next': step_names['build_generate_report' if self.report_type else 'build_add_result'] #pylint:disable=line-too-long
                }
            ],
            Default=step_names['wait'],
        )

        if self.report_type:
            steps[step_names['build_generate_report']] = PassState(
                Result={
                    'path':'/reports/generate',
                    'body':{
                        'out_path': '$.next.out_path',
                        'report_type': '$.next.report_type'
                        },
                    'method': 'POST'
                },
                ResultPath='$.api_call',
                Next=step_names['generate_report']
            )

            steps[step_names['generate_report']] = TaskState(
                Resource=get_arn('lambda', f'function:drench-sdk-call-api:{sdk_version}'),
                Next=step_names['build_add_result'],
                ResultPath='$.result.report_url',
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

        added_step = {
            'name': '$.next.name',
            'out_path': '$.next.out_path',
            'content_type': '$.next.content_type',
            'status': '$.result.status',
        }

        if self.report_type:
            added_step['report_url'] = '$.result.report_url'


        steps[step_names['build_add_result']] = PassState(
            Result={
                'path':'/jobs/$.job_id/steps',
                'body':{
                    'step':added_step,
                },
                'method': 'PUT'
            },
            ResultPath='$.api_call',
            Next=step_names['add_result']
        )

        steps[step_names['add_result']] = TaskState(
            Resource=get_arn('lambda', f'function:drench-sdk-call-api:{sdk_version}'),
            Next=step_names['finish_choice'],
            ResultPath='$.api_result',
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
