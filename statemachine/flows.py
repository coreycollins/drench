from states import TaskState, State, WaitState, PassState, ChoiceState

class Flow(object):
    """docstring for Flow."""
    def __init__(self, Name, OnSucceed, OnFail, Resources=None):
        self.Name = Name
        self.OnSucceed = OnSucceed
        self.OnFail = OnFail
        self.Resources = Resources

    def states(self):
        pass

    def get_resource(self, name):
        if (self.Resources):
            return self.Resources[name]
        else:
            raise BaseException("No resources were applied to this flow.")

class SNSFlow(Flow):
    """docstring for ."""
    def __init__(self, TopicArn, Subject, Message, **kwargs):
        super(SNSFlow, self).__init__(**kwargs)
        self.TopicArn = TopicArn
        self.Subject = Subject
        self.Message = Message

    def states(self):
        states = {}
        states[self.Name] = PassState(
            Next='%s.2.send' % self.Name,
            Result={
                'arn': self.TopicArn,
                'subject': self.Subject,
                'message': self.Message
            },
            ResultPath='$.sns'
        )

        states['%s.2.send' % self.Name] = State=TaskState(
            Resource=self.get_resource('send_sns'),
            Next=self.OnSucceed
        )

        return states

class BatchFlow(Flow):
    """docstring for ."""
    def __init__(self, JobQueue, JobDefinition, Parameters=None, ContainerOverrides=None, **kwargs):
        super(BatchFlow, self).__init__(**kwargs)
        self.JobQueue = JobQueue
        self.JobDefinition = JobDefinition
        self.Parameters = Parameters
        self.ContainerOverrides = ContainerOverrides

    def states(self):
        setup = {
            'jobName': self.Name,
            'jobQueue':self.JobQueue,
            'jobDefinition': self.JobDefinition
        }
        if (self.Parameters):
            setup['parameters'] = self.Parameters

        if (self.ContainerOverrides):
            setup['containerOverrides'] = self.ContainerOverrides

        states = {}

        states[self.Name] = PassState(
            Result=setup,
            ResultPath='$.batch',
            Next='%s.2.run' % self.Name
        )

        states['%s.2.run' % self.Name] = TaskState(
            Resource=self.get_resource('run_batch'),
            Next='%s.3.wait' % self.Name,
            ResultPath='$.batch.jobId'
        )

        states['%s.3.wait' % self.Name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.Name
        )

        states['%s.4.check' % self.Name] = TaskState(
            Resource=self.get_resource('check_batch'),
            Next='%s.5.choice' % self.Name,
            ResultPath="$.batch.status",
            Retry=[
                  "ErrorEquals": [ "Lambda.Unknown" ],
                  "IntervalSeconds": 30,
                  "MaxAttempts": 5,
                  "BackoffRate": 1.5
            ]
        )

        states['%s.5.choice' % self.Name] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.batch.status",
                    "StringEquals": "FAILED",
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.batch.status",
                  "StringEquals": "SUCCEEDED",
                  "Next": self.OnSucceed
                }
            ],
            Default='%s.3.wait' % self.Name
        )

        return states

class GlueFlow(Flow):
    """docstring for ."""
    def __init__(self, JobName, Arguments=None, AllocatedCapacity=1, **kwargs):
        super(GlueFlow, self).__init__(**kwargs)
        self.JobName = JobName
        self.Arguments = Arguments
        self.AllocatedCapacity = AllocatedCapacity

    def states(self):
        setup = {
            'JobName': self.JobName,
            'AllocatedCapacity': self.AllocatedCapacity
        }
        if (self.Arguments):
            setup['Arguments'] = self.Arguments

        states = {}

        states[self.Name] = PassState(
            Result=setup,
            ResultPath='$.glue',
            Next='%s.2.run' % self.Name
        )

        states['%s.2.run' % self.Name] = TaskState(
            Resource=self.get_resource('run_glue'),
            Next='%s.3.wait' % self.Name,
            ResultPath='$.glue.runId'
        )

        states['%s.3.wait' % self.Name] = WaitState(
            Seconds=200,
            Next='%s.4.check' % self.Name
        )

        states['%s.4.check' % self.Name] = TaskState(
            Resource=self.get_resource('check_glue'),
            Next='%s.5.choice' % self.Name,
            ResultPath="$.glue.status",
            Retry=[
                  "ErrorEquals": [ "Lambda.Unknown" ],
                  "IntervalSeconds": 30,
                  "MaxAttempts": 5,
                  "BackoffRate": 1.5
            ]
        )

        states['%s.5.choice' % self.Name] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.glue.status",
                    "StringEquals": "FAILED",
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.glue.status",
                  "StringEquals": "SUCCEEDED",
                  "Next": self.OnSucceed
                }
            ],
            Default='%s.3.wait' % self.Name
        )

        return states
