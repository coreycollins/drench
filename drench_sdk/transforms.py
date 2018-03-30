"""flows are fucntion-like packages of states"""
from drench_sdk.resources import Resources
from drench_sdk.states import State, TaskState, WaitState, PassState, ChoiceState

#pylint:disable=too-few-public-methods
#pylint:disable=invalid-name

RESOURCES = Resources()

class Transform(State):
    """docstring for Transform."""
    def __init__(self, name, in_taxonomy, out_taxonomy, start=False, **kwargs):
        super(Transform, self).__init__(Type='meta', **kwargs)
        self.name = name
        self.in_taxonomy = in_taxonomy
        self.out_taxonomy = out_taxonomy
        self.start = start

    def states(self):
        """return compenent state objects"""
        pass

class SNSTransform(Transform):
    """docstring for ."""
    def __init__(self, TopicArn, Subject, Message, **kwargs):
        super(SNSTransform, self).__init__(**kwargs)
        self.TopicArn = TopicArn
        self.Subject = Subject
        self.Message = Message
        self.can_fail = False

    def states(self):
        states = {}
        states[self.name] = PassState(
            Next='%s.2.send' % self.name,
            Result={
                'arn': self.TopicArn,
                'subject': self.Subject,
                'message': self.Message
            },
            ResultPath='$.sns'
        )

        states['%s.2.send' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'send_sns'),
            Next=self.Next
        )

        return states

class BatchTransform(Transform):
    """docstring for ."""
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchTransform, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters
        self.on_fail = None

    def states(self):
        setup = {
            'jobname': self.name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition
        }

        if self.parameters:
            setup['parameters'] = self.parameters

        states = {}

        states[self.name] = PassState(
            Result=setup,
            ResultPath='$.batch',
            Next='%s.2.run' % self.name,
        )

        states['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-run_batch'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.batch.jobId'
        )

        states['%s.3.wait' % self.name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.name
        )

        states['%s.4.check' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-check_batch'),
            Next='%s.5.choice' % self.name,
            ResultPath="$.batch.status",
            Retry=[{
                "ErrorEquals": ["Lambda.Unknown"],
                "IntervalSeconds": 30,
                "MaxAttempts": 5,
                "BackoffRate": 1.5
            }]
        )

        states['%s.5.choice' % self.name] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.batch.status",
                    "StringEquals": "FAILED",
                    "Next": self.on_fail
                },
                {
                    "Variable": "$.batch.status",
                    "StringEquals": "SUCCEEDED",
                    "Next": self.Next
                }
            ],
            Default='%s.3.wait' % self.name
        )

        return states

class GlueTransform(Transform):
    """docstring for ."""
    def __init__(self, Jobname, Arguments=None, AllocatedCapacity=1, **kwargs):
        super(GlueTransform, self).__init__(**kwargs)
        self.Jobname = Jobname
        self.Arguments = Arguments
        self.AllocatedCapacity = AllocatedCapacity
        self.on_fail = None

    def states(self):
        setup = {
            'JobName': self.Jobname,
            'AllocatedCapacity': self.AllocatedCapacity
        }
        if self.Arguments:
            setup['Arguments'] = self.Arguments

        states = {}

        states[self.name] = PassState(
            Result=setup,
            ResultPath='$.glue',
            Next='%s.2.run' % self.name
        )

        states['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-run_glue'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.glue.runId'
        )

        states['%s.3.wait' % self.name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.name
        )

        states['%s.4.check' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-check_glue'),
            Next='%s.5.choice' % self.name,
            ResultPath="$.glue.status",
            Retry=[{
                "ErrorEquals": ["Lambda.Unknown"],
                "IntervalSeconds": 30,
                "MaxAttempts": 5,
                "BackoffRate": 1.5
            }]
        )

        states['%s.5.choice' % self.name] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.glue.status",
                    "StringEquals": "FAILED",
                    "Next": self.on_fail
                },
                {
                    "Variable": "$.glue.status",
                    "StringEquals": "SUCCEEDED",
                    "Next": self.Next
                }
            ],
            Default='%s.3.wait' % self.name
        )

        return states

class QueryTransform(Transform):
    """docstring for ."""
    def __init__(self, QueryString, QueryExecutionContext=None, ResultConfiguration=None, **kwargs):
        super(QueryTransform, self).__init__(**kwargs)
        self.QueryString = QueryString
        self.QueryExecutionContext = QueryExecutionContext
        self.ResultConfiguration = ResultConfiguration
        self.on_fail = None

    def states(self):
        setup = {
            'QueryString': self.QueryString,
            'QueryExecutionContext': self.QueryExecutionContext,
            'ResultConfiguration': self.ResultConfiguration
        }

        states = {}

        states[self.name] = PassState(
            Result=setup,
            ResultPath='$.query',
            Next='%s.2.run' % self.name
        )

        states['%s.2.run' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-run_query'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.query.QueryExecutionId'
        )

        states['%s.3.wait' % self.name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.name
        )

        states['%s.4.check' % self.name] = TaskState(
            Resource=RESOURCES.get_arn('lambda', 'function', 'development-check_query'),
            Next='%s.5.choice' % self.name,
            ResultPath="$.query.status",
            Retry=[{
                "ErrorEquals": ["Lambda.Unknown"],
                "IntervalSeconds": 30,
                "MaxAttempts": 5,
                "BackoffRate": 1.5
            }]
        )

        states['%s.5.choice' % self.name] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.query.status",
                    "StringEquals": "FAILED",
                    "Next": self.on_fail
                },
                {
                    "Variable": "$.query.status",
                    "StringEquals": "CANCELLED",
                    "Next": self.on_fail
                },
                {
                    "Variable": "$.query.status",
                    "StringEquals": "SUCCEEDED",
                    "Next": self.Next
                }
            ],
            Default='%s.3.wait' % self.name
        )

        return states
