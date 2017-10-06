from states import TaskState, State, WaitState, PassState, ChoiceState

class Flow(object):
    """docstring for Flow."""
    def __init__(self, Name, OnSucceed, OnFail, Resources=None):
        self.Name = Name
        self.OnSucceed = OnSucceed
        self.OnFail = OnFail
        self.Resources = Resources

    def prefix(self):
        return '%s.%s' % (self.__class__.__name__, self.Name)

    def start(self):
        pass

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

    def start(self):
        return ('%s.1.setup' % self.prefix())

    def states(self):
        states = {}
        states[self.start()] = PassState(
            Result={
                'arn': self.TopicArn,
                'subject': self.Subject,
                'message': self.Message
            },
            ResultPath='$.sns'
        )

        states['%s.2.send' % self.prefix()] = State=TaskState(
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

    def start(self):
        return ('%s.1.setup' % self.prefix())

    def states(self):
        setup = {
            'jobName': self.prefix(),
            'jobQueue':self.JobQueue,
            'jobDefinition': self.JobDefinition
        }
        if (self.Parameters):
            setup['parameters'] = self.Parameters

        if (self.ContainerOverrides):
            setup['containerOverrides'] = self.ContainerOverrides

        states = {}

        states[self.start()] = PassState(
            Result=setup,
            ResultPath='$.batch',
            Next='%s.2.run' % self.prefix()
        )

        states['%s.2.run' % self.prefix()] = TaskState(
            Resource=self.get_resource('run_batch'),
            Next='%s.3.wait' % self.prefix(),
            ResultPath='$.batch.jobId'
        )

        states['%s.3.wait' % self.prefix()] = WaitState(
            Seconds=30,
            Next='%s.4.check' % self.prefix()
        )

        states['%s.4.check' % self.prefix()] = TaskState(
            Resource=self.get_resource('check_batch'),
            Next='%s.5.choice' % self.prefix(),
            ResultPath="$.batch.status"
        )

        states['%s.5.choice' % self.prefix()] = ChoiceState(
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
            Default='%s.3.wait' % self.prefix()
        )

        return states
