from .states import TaskState, State, WaitState, PassState, ChoiceState
from .resources import Resources

class Flow(object):
    """docstring for Flow."""
    def __init__(self, Name, OnSucceed, OnFail):
        self.Name = Name
        self.OnSucceed = OnSucceed
        self.OnFail = OnFail

    def prefix(self):
        return '%s.%s' % (self.__class__.__name__, self.Name)

    def start(self):
        pass


class BatchFlow(Flow):
    """docstring for ."""
    def __init__(self, JobQueue, JobDefinition, Parameters=None, ContainerOverrides=None, **kwargs):
        super(BatchFlow, self).__init__(**kwargs)
        self.JobQueue = JobQueue
        self.JobDefinition = JobDefinition
        self.Parameters = Parameters
        self.ContainerOverrides = ContainerOverrides

    def start(self):
        return '%s.1.setup' % self.prefix()

    def states(self):
        resources = Resources()

        setup = {
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
            ResultPath='$.%s' % self.prefix(),
            Next='%s.2.run' % self.prefix()
        )

        states['%s.2.run' % self.prefix()] = TaskState(
            InputPath='$.%s' % self.prefix(),
            Resource=resources.get('aws_lambda_run_batch'),
            Next='%s.3.wait' % self.prefix(),
            ResultPath='$.jobId'
        )

        states['%s.3.wait' % self.prefix()] = WaitState(
            Seconds=30,
            Next='%s.4.check' % self.prefix()
        )

        states['%s.4.check' % self.prefix()] = TaskState(
            Resource=resources.get('aws_lambda_check_batch'),
            Next='%s.5.choice' % self.prefix(),
            ResultPath="$.status"
        )

        states['%s.5.choice' % self.prefix()] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.status",
                    "StringEquals": "FAILED",
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.status",
                  "StringEquals": "SUCCEEDED",
                  "Next": self.OnSucceed
                }
            ],
            Default='%s.3.wait' % self.prefix()
        )

        return states
