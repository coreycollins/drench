""" sample_wf.py """
from drench_sdk import WorkFlow, Transform

workflow = WorkFlow()

workflow.add_state(
    name='hello-world',
    start=True,
    state=Transform('arn:aws:lambda:us-east-1:909533743566:function:test')
)


if __name__ == '__main__':
    workflow.run()
