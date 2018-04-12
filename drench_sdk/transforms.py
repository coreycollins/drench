'''flows are fucntion-like packages of states'''
from drench_sdk.resources import Resources
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

RESOURCES = Resources()

class Transform(State):
    '''docstring for Transform.'''
    def __init__(self, name, task, report=False, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name
        self.task = task
        self.report = report

        # defaults to be over-ridden
        self.wait_seconds = 60
        self.on_fail = None
        self.next = None

        self.steps = {}

    def setup(self):
        '''placeholder for inheritor classes to populate'''
        pass

    def states(self):
        '''compile and return all steps in the transform'''
        self.steps = {}

        self.steps[f'{self.name}.1.setup'] = PassState(
            Result=self.setup(),
            ResultPath='$.next',
            Next=f'{self.name}.2.run'
        )

        self.steps[f'{self.name}.2.run'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-run_task'),
            Next=f'{self.name}.3.wait',
            ResultPath='$'
        )

        self.steps[f'{self.name}.3.wait'] = WaitState(
            Seconds=self.wait_seconds,
            Next=f'{self.name}.4.check',
        )


        self.steps[f'{self.name}.4.check'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', f'function:development-check_task'),
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
                            'Variable': f'$.{self.task}.status',
                            'StringEquals': 'FAILED',
                        },
                        {
                            'Variable': f'$.{self.task}.status',
                            'StringEquals': 'SUCCEEDED',
                        }
                    ],

                    'Next': f'{self.name}.6.add_result'
                }
            ],
            Default=f'{self.name}.{len(self.steps)-1}.wait'
        )

        self.steps[f'{self.name}.6.add_result'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-add_result'),
            Next=self.Next,
            ResultPath='$.add_result.status',
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
                    'Variable': f'$.result.status',
                    'StringEquals': 'SUCCEEDED',
                    'Next': self.next
                }
            ],
            Default=self.on_fail
            )

        return self.steps

#class SNSTransform(Transform):
#    '''docstring for .'''
#    def __init__(self, TopicArn, Subject, Message, **kwargs):
#        super(SNSTransform, self).__init__(task='sns', **kwargs)
#        self.TopicArn = TopicArn
#        self.Subject = Subject
#        self.Message = Message
#
#    def states(self):
#        self.steps[self.name] = PassState(
#            Next='%s.2.send' % self.name,
#            Result={
#                'arn': self.TopicArn,
#                'subject': self.Subject,
#                'message': self.Message
#            },
#            ResultPath='$.sns'
#        )
#
#        self.steps['%s.2.send' % self.name] = TaskState(
#            Resource=RESOURCES.get_arn('lambda', 'function:send_sns'),
#            Next=self.Next
#        )
#
#        return self.steps

#class BatchTransform(Transform):
#    '''docstring for .'''
#    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
#        super(BatchTransform, self).__init__(task='batch', **kwargs)
#        self.job_queue = job_queue
#        self.job_definition = job_definition
#        self.parameters = parameters
#
#    def states(self):
#        setup = {
#            'jobname': self.name,
#            'jobQueue':self.job_queue,
#            'jobDefinition': self.job_definition
#        }
#
#        if self.parameters:
#            setup['parameters'] = self.parameters
#
#
#        self.steps[self.name] = PassState(
#            Result=setup,
#            ResultPath='$.batch',
#            Next='%s.2.run' % self.name,
#        )
#
#        self.steps['%s.2.run' % self.name] = TaskState(
#            Resource=RESOURCES.get_arn('lambda', 'function:development-run_batch'),
#            Next='%s.3.wait' % self.name,
#            ResultPath='$.batch.jobId'
#        )
#
#        self.append_wait_result_choice(wait_seconds=180)
#
#        return self.steps


class GlueTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_name, arguments=None, allocated_capacity=1, **kwargs):
        super(GlueTransform, self).__init__(task='glue', **kwargs)
        self.job_name = job_name
        self.arguments = arguments
        self.allocated_capacity = allocated_capacity

    def setup(self):
        setup = {
            'name': self.name,
            'type': self.task,
            'params': {
                'JobName': self.job_name,
                'Allocated_capacity': self.allocated_capacity
            },
            'report': self.report
        }

        setup['params']['arguments'] = {
            '--in_path':'$.next.in_path',
            '--out_path':'$.next.out_path'
        }

        if self.arguments:
            setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.arguments}

        return setup


#class QueryTransform(Transform):
#    '''docstring for .'''
#    def __init__(self, QueryString, database, **kwargs):
#        super(QueryTransform, self).__init__(task='query', **kwargs)
#        self.QueryString = QueryString
#        self.QueryExecutionContext = {'Database': database}
#        self.ResultConfiguration = {'OutputLocation': ''}
#
#    def states(self):
#        setup = {
#            'QueryString': self.QueryString,
#            'QueryExecutionContext': self.QueryExecutionContext,
#            'ResultConfiguration': self.ResultConfiguration
#        }
#
#        self.steps[self.name] = PassState(
#            Result=setup,
#            ResultPath='$.query',
#            Next='%s.2.run' % self.name
#        )
#
#        self.steps['%s.2.run' % self.name] = TaskState(
#            Resource=RESOURCES.get_arn('lambda', 'function:development-run_query'),
#            Next='%s.3.wait' % self.name,
#            ResultPath='$.query.QueryExecutionId'
#        )
#
#        self.append_wait_result_choice(wait_seconds=30)
#
#        return self.steps
