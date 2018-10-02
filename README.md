## Drench

Drench is a lightweight python sdk that can be used to programmatically build serverless workflows on AWS.

Similar to [Airflow](https://github.com/apache/incubator-airflow), you can build workflows that describe a directed acyclic graphs (DAGs) of steps. It uses AWS Step Functions under the hood to build a state machine that can execute different severless functions via calls to predefined lambda functions.

Its goal is to provide a way to orchestrate your serverless tasks that is simple and easy to organize.

### Getting started

Install drench with pip. Python2.7+ is supported.

```
$ pip install drench
```

Publish the Drench lambda functions used to execute states in your workflow to your AWS region. This will place a file called **drench.json** in your root directory which contains the resource arns. This is needed by Drench to run your workflows.

```
$ drench init
```

Build a simple workflow that executes a custom lambda function.

```python
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
```

To execute the workflow call the `run` command. Drench will create a step function on AWS and run it. It uses boto3 to call AWS and reads your credntials from the default location boto3 expects. You can set these manually by passing them in as environment variables. See [boto3](http://boto3.readthedocs.io) documentation for more details.

```
$ python sample_wf.py
```

For a more in depth overview, you can read the [documentation](http://example.com).

### TODO

* [ ] Ability to create parallel steps.
* [ ] Better error handling
* [ ] More examples

### Links

* [Documentation](http://example.com)
* [Boto3](http://boto3.readthedocs.io)

### Authors

Corey Collins (@coreycollins)
Ed Jaros (@ejaros)

### License

MIT.
