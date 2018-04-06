'''flows are fucntion-like packages of states'''
from drench_sdk.resources import Resources
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

#pylint:disable=too-few-public-methods
#pylint:disable=invalid-name

RESOURCES = Resources()

class Transform(State): #pylint:disable=too-many-instance-attributes
    '''docstring for Transform.'''
    def __init__(self, name, output_data, input_data=None, on_fail=None, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name
        self.out_path = output_data['path']
        self.out_taxonomy = output_data['taxonomy']

        if input_data:
            self.in_path = input_data['path']
            self.in_taxonomy = input_data['taxonomy']

        self.on_fail = on_fail
        self.pool_id = None # set by WorkFlow.addTransform

        self.steps = {}

    def states(self):
        '''compile and return all steps in the transform'''
        pass

    def append_wait_result_choice(self, task_type, wait_seconds):
        '''add consistent pattern after task states'''

        self.steps[f'{self.name}.{len(self.steps)+1}.wait'] = WaitState(
            Seconds=wait_seconds,
            Next=f'{self.name}.{len(self.steps)+2}.check_{task_type}',
        )


        self.steps[f'{self.name}.{len(self.steps)+1}.check_{task_type}'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', f'function:development-check_{task_type}'),
            Next=f'{self.name}.{len(self.steps)+2}.choice',
            ResultPath=f'$.{task_type}.status',
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
                            'Variable': f'$.{task_type}.status',
                            'StringEquals': 'FAILED',
                        },
                        {
                            'Variable': f'$.{task_type}.status',
                            'StringEquals': 'SUCCEEDED',
                        }
                    ],

                    'Next': f'{self.name}.{len(self.steps)+2}.pass_params'
                }
            ],
            Default=f'{self.name}.{len(self.steps)-1}.wait'
        )

        self.steps[f'{self.name}.{len(self.steps)+1}.pass_params'] = PassState(
            Result={
                'job_id': '1234', #TODO: discuss where this comes from
                'name': self.name,
                'output_path': self.out_path,
                'output_taxonomy': self.out_taxonomy,
                'type': task_type,
                'state': f'$.{task_type}.status',
                },
            ResultPath='$.payload',
            Next=f'{self.name}.{len(self.steps)+2}.add_result'
        )

        self.steps[f'{self.name}.{len(self.steps)+1}.add_result'] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-add_result'),
            Next=f'{self.name}.{len(self.steps)+2}.choice',
            ResultPath='$.add_result.status',
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
                    'Variable': '$.add_result.status',
                    'StringEquals': 'FAILED',
                    'Next': self.on_fail
                },
                {
                    'Variable': '$.add_result.status',
                    'StringEquals': 'SUCCEEDED',
                    'Next': self.Next
                }
            ],
            Default=self.on_fail
        )



class SNSTransform(Transform):
    '''docstring for .'''
    def __init__(self, TopicArn, Subject, Message, **kwargs):
        super(SNSTransform, self).__init__(**kwargs)
        self.TopicArn = TopicArn
        self.Subject = Subject
        self.Message = Message

    def states(self):
        self.steps[self.name] = PassState(
            Next='%s.2.send' % self.name,
            Result={
                'arn': self.TopicArn,
                'subject': self.Subject,
                'message': self.Message
            },
            ResultPath='$.sns'
        )

        self.steps['%s.2.send' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:send_sns'),
            Next=self.Next
        )

        return self.steps


class BatchTransform(Transform):
    '''docstring for .'''
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchTransform, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters

    def states(self):
        setup = {
            'jobname': self.name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition
        }

        if self.parameters:
            setup['parameters'] = self.parameters


        self.steps[self.name] = PassState(
            Result=setup,
            ResultPath='$.batch',
            Next='%s.2.run' % self.name,
        )

        self.steps['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-run_batch'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.batch.jobId'
        )

        self.append_wait_result_choice('batch', 180)

        return self.steps


class GlueTransform(Transform):
    '''docstring for .'''
    def __init__(self, Jobname, Arguments=None, AllocatedCapacity=1, **kwargs):
        super(GlueTransform, self).__init__(**kwargs)
        self.Jobname = Jobname
        self.Arguments = Arguments
        self.AllocatedCapacity = AllocatedCapacity

    def states(self):
        setup = {
            'JobName': self.Jobname,
            'AllocatedCapacity': self.AllocatedCapacity
        }
        if self.Arguments:
            setup['Arguments'] = self.Arguments

        self.steps = {}

        self.steps[self.name] = PassState(
            Result=setup,
            ResultPath='$.glue',
            Next='%s.2.run' % self.name
        )

        self.steps['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-run_glue'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.glue.runId'
        )

        self.append_wait_result_choice('glue', 600)

        return self.steps

class QueryTransform(Transform):
    '''docstring for .'''
    def __init__(self, QueryString, database, **kwargs):
        super(QueryTransform, self).__init__(**kwargs)
        self.QueryString = QueryString
        self.QueryExecutionContext = {'Database': database}
        self.ResultConfiguration = {'OutputLocation': self.out_path}

    def states(self):
        setup = {
            'QueryString': self.QueryString,
            'QueryExecutionContext': self.QueryExecutionContext,
            'ResultConfiguration': self.ResultConfiguration
        }

        self.steps[self.name] = PassState(
            Result=setup,
            ResultPath='$.query',
            Next='%s.2.run' % self.name
        )

        self.steps['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function:development-run_query'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.query.QueryExecutionId'
        )

        self.append_wait_result_choice('query', 30)

        return self.steps
