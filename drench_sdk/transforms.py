'''flows are fucntion-like packages of states'''
from drench_sdk.resources import Resources
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

#pylint:disable=too-few-public-methods
#pylint:disable=invalid-name

RESOURCES = Resources()

class Transform(State): #pylint:disable=too-many-instance-attributes
    '''docstring for Transform.'''
    def __init__(self, name, task, input_path=None, on_fail=None, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name

        if input_path:
            self.in_path = input_path

        self.on_fail = on_fail
        self.wait_seconds = 60 #default to be over-ridden
        self.task = task

        self.steps = {}

    def setup(self):
        '''placeholder for inheritor classes to populate'''
        pass

    def states(self):
        '''compile and return all steps in the transform'''
        self.steps = {}

        self.steps[self.name] = PassState(
            Result=self.setup(),
            ResultPath='$.next',
            Next='%s.2.run' % self.name
        )

        self.steps['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-run_task'),
            Next='%s.3.wait' % self.name,
            ResultPath='$'
        )

        self.steps[f'{self.name}.{len(self.steps)+1}.wait'] = WaitState(
            Seconds=self.wait_seconds,
            Next=f'{self.name}.{len(self.steps)+2}.check_{self.task}',
        )


        self.steps[f'{self.name}.{len(self.steps)+1}.check_{self.task}'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', f'function:development-check_{self.task}'),
            Next=f'{self.name}.{len(self.steps)+2}.choice',
            ResultPath=f'$.result.status',
            Retry=[{
                'ErrorEquals': ['Lambda.Unknown'],
                'IntervalSeconds': 30,
                'MaxAttempts': 5,
                'BackoffRate': 1.5
            }]
        )

        self.steps[f'{self.name}.{len(self.steps)+1}.choice'] = ChoiceState(
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

                    'Next': f'{self.name}.{len(self.steps)+2}.pass_params'
                }
            ],
            Default=f'{self.name}.{len(self.steps)-1}.wait'
        )

        self.steps[f'{self.name}.{len(self.steps)+1}.add_result'] = TaskState(
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
    def __init__(self, Jobname, Arguments=None, AllocatedCapacity=1, **kwargs):
        super(GlueTransform, self).__init__(task='glue', **kwargs)
        self.Jobname = Jobname
        self.Arguments = Arguments
        self.AllocatedCapacity = AllocatedCapacity

    def setup(self):
        setup = {
            'name': self.name,
            'type': self.task,
            'params': {
                'JobName': self.Jobname,
                'AllocatedCapacity': self.AllocatedCapacity
            }
        }

        setup['params']['Arguments'] = {
            '--in_path':'$.next.in_path',
            '--out_path':'$.next.out_path'
        }

        if self.Arguments:
            setup['params']['Arguments'] = {**setup['params']['Arguments'], **self.Arguments}

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
