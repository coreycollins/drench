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

        states = [
            PassState(
                Name='%s.setup' % prefix,
                Result=setup,
                ResultPath='$.%s' % prefix,
                Next='%s.run' % prefix
            ),
            TaskState(
                Name='%s.run' % prefix,
                Resource='arn:batch',
                Next='%s.wait' % prefix
            ),
            WaitState(
                Name='%s.wait' % prefix,
                Seconds=30,
                Next='%s.status' % prefix
            ),
            TaskState(
                Name='%s.status' % prefix,
                Resource='arn:get:job:status',
                Next='%s.choice' % prefix,
                ResultPath="$.%s.status" % prefix
            ),
            ChoiceState(
                Name='%s.choice' % prefix,
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
                Default='%s.wait' % prefix
            )
        ]

        return states
