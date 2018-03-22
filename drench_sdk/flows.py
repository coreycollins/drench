"""flows are fucntion-like packages of states"""
from resources import Resources
from states import TaskState, WaitState, PassState, ChoiceState

resources = Resources()

class Flow(object):
    """docstring for Flow."""
    def __init__(self, name, in_taxonomy, out_taxonomy, on_succeed=None, start=False):
        self.name = name
        self.in_taxonomy = in_taxonomy
        self.out_taxonomy = out_taxonomy
        self.start = start
        self.on_succeed = on_succeed

    def states(self):
        """return compenent state objects"""
        pass

class SNSFlow(Flow):
    """docstring for ."""
    def __init__(self, TopicArn, Subject, Message, **kwargs):
        super(SNSFlow, self).__init__(**kwargs)
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

        states['%s.2.send' % self.name] = State=TaskState(
            Resource=resources.get_arn('lambda', 'send_sns'),
            Next=self.on_succeed
        )

        return states

class BatchFlow(Flow):
    """docstring for ."""
    def __init__(self, job_queue, job_definition, parameters=None, **kwargs):
        super(BatchFlow, self).__init__(**kwargs)
        self.job_queue = job_queue
        self.job_definition = job_definition
        self.parameters = parameters

    def states(self):
        setup = {
            'jobname': self.name,
            'jobQueue':self.job_queue,
            'jobDefinition': self.job_definition
        }

        if (self.parameters):
            setup['parameters'] = self.parameters

        states = {}

        states[self.name] = PassState(
            Result=setup,
            ResultPath='$.batch',
            Next='%s.2.run' % self.name,
        )

        states['%s.2.run' % self.name] = TaskState(
            Resource=resources.get_arn('lambda', 'run_batch'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.batch.jobId'
        )

        states['%s.3.wait' % self.name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.name
        )

        states['%s.4.check' % self.name] = TaskState(
            Resource=resources.get_arn('lambda', 'check_batch'),
            Next='%s.5.choice' % self.name,
            ResultPath="$.batch.status",
            Retry=[{
              "ErrorEquals": [ "Lambda.Unknown" ],
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
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.batch.status",
                  "StringEquals": "SUCCEEDED",
                  "Next": self.on_succeed
                }
            ],
            Default='%s.3.wait' % self.name
        )

        return states

class GlueFlow(Flow):
    """docstring for ."""
    def __init__(self, Jobname, Arguments=None, AllocatedCapacity=1, **kwargs):
        super(GlueFlow, self).__init__(**kwargs)
        self.Jobname = Jobname
        self.Arguments = Arguments
        self.AllocatedCapacity = AllocatedCapacity

    def states(self):
        setup = {
            'Jobname': self.Jobname,
            'AllocatedCapacity': self.AllocatedCapacity
        }
        if (self.Arguments):
            setup['Arguments'] = self.Arguments

        states = {}

        states[self.name] = PassState(
            Result=setup,
            ResultPath='$.glue',
            Next='%s.2.run' % self.name
        )

        states['%s.2.run' % self.name] = TaskState(
            Resource=resources.get_arn('lambda', 'run_glue'),
            Next='%s.3.wait' % self.name,
            ResultPath='$.glue.runId'
        )

        states['%s.3.wait' % self.name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.name
        )

        states['%s.4.check' % self.name] = TaskState(
            Resource=resources.get_arn('lambda', 'check_glue'),
            Next='%s.5.choice' % self.name,
            ResultPath="$.glue.status",
            Retry=[{
              "ErrorEquals": [ "Lambda.Unknown" ],
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
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.glue.status",
                  "StringEquals": "SUCCEEDED",
                  "Next": self.on_succeed
                }
            ],
            Default='%s.3.wait' % self.name
        )

        return states
