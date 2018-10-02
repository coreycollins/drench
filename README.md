## Drench

Drench is a lightweight python sdk that can be used to programmatically build serverless workflows on AWS.

Similar to [Airflow](https://github.com/apache/incubator-airflow), you can build workflows that describe a directed acyclic graphs (DAGs) of steps. It uses AWS Step Functions under the hood to build a state machine that can execute different serverless functions via calls to predefined lambda functions.

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

For a more in depth overview, you can read the [documentation](http://drench.io).

### TODO

* [ ] Ability to create parallel steps.
* [ ] Better error handling
* [ ] More examples

### Links

* [Documentation](http://example.com)
* [Boto3](http://boto3.readthedocs.io)

### Authors

* Corey Collins (@coreycollins)
* Ed Jaros (@ejaros)

### License

MIT.
