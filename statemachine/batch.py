from .states import TaskState, State, WaitState, PassState, ChoiceState

class BatchFlow(object):
    """docstring for ."""
    def __init__(self, Name, JobQueue, JobDefinition, OnSucceed, OnFail, Parameters=None, ContainerOverrides=None):
        self.Name = Name
        self.JobQueue = JobQueue
        self.JobDefinition = JobDefinition
        self.Parameters = Parameters
        self.ContainerOverrides = ContainerOverrides
        self.OnSucceed = OnSucceed
        self.OnFail = OnFail

    def states(self):
        prefix = 'batch.%s' % self.Name
        setup = {
            'jobQueue':self.JobQueue,
            'jobDefinition': self.JobDefinition
        }
        if (self.Parameters):
            setup['parameters'] = self.Parameters
        if (self.ContainerOverrides):
            setup['containerOverrides'] = self.ContainerOverrides

        states = {}

        states['%s.1setup' % prefix] = PassState(
            Result=setup,
            ResultPath='$.%s' % prefix,
            Next='%s.2run' % prefix
        )

        states['%s.2run' % prefix] = TaskState(
            Resource='arn:batch',
            Next='%s.3wait' % prefix
        )

        states['%s.3wait' % prefix] = WaitState(
            Seconds=30,
            Next='%s.4status' % prefix
        )

        states['%s.4status' % prefix] = TaskState(
            Resource='arn:get:job:status',
            Next='%s.5choice' % prefix,
            ResultPath="$.%s.status" % prefix
        )

        states['%s.5choice' % prefix] = ChoiceState(
            Choices=[
                {
                    "Variable": "$.%s.status" % prefix,
                    "StringEquals": "FAILED",
                    "Next": self.OnFail
                },
                {
                  "Variable": "$.%s.status" % prefix,
                  "StringEquals": "SUCCEEDED",
                  "Next": self.OnSucceed
                }
            ],
            Default='%s.6wait' % prefix
        )

        return states
