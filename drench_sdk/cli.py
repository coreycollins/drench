''' SDK CLI '''
#!/usr/bin/env python

import os
import sys
import importlib
import time
import json
import uuid
import boto3
import click
import requests

def _load_workflow(filepath, args):
    """ Load the file and call the main method """
    module_path = os.path.dirname(filepath)
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    sys.path.insert(0, module_path)

    # Load the wf
    module = importlib.import_module(module_name)
    return module.main(args)

def _sfn_waiter(execution_arn):
    """ Wait for sfn machine to exit """
    client = boto3.client('stepfunctions')
    while True:
        res = client.describe_execution(executionArn=execution_arn)

        if res['status'] == 'SUCCEEDED':
            return res['output']
        elif res['status'] in ['FAILED', 'TIMED_OUT', 'ABORTED']:
            raise click.ClickException('Error running statemachine')

        time.sleep(1)

@click.group()
def cli():
    """ command group for drench_sdk """
    pass

@cli.command('output', short_help='Generate output for a drench sdk workflow.')
@click.option('--terraform', '-t', default=False, is_flag=True, help='Generate this output for terraform')
@click.argument('filename', required=True)
@click.argument('args', nargs=-1)
def output(filename, terraform, args):
    """ Generate a workflow and print it's output. """
    full_path = os.path.join(os.curdir, filename)
    workflow = _load_workflow(full_path, args)

    # Print the workflow to JSON
    if terraform:
        print(json.dumps({'machine':workflow.to_json()}))
    else:
        click.echo(click.style(json.dumps(workflow.as_dict(), indent=4), fg='blue'))

@cli.command('run', short_help='Test a workflow.')
@click.option('--param', '-p', nargs=2, type=click.Tuple([str, str]), multiple=True)
@click.option('--topic_arn', required=True)
@click.option('--role_arn', required=True)
@click.argument('filename', required=True)
@click.argument('args', nargs=-1)
def run(filename, topic_arn, role_arn, param, args):
    """ Run a workflow by executing a test statemachine. """
    full_path = os.path.join(os.curdir, filename)
    workflow = _load_workflow(full_path, args)

    client = boto3.client('stepfunctions')
    click.echo(click.style('Creating state machine...', fg='blue'))
    resp = client.create_state_machine(
        name=uuid.uuid4().hex,
        definition=workflow.to_json(),
        roleArn=role_arn
    )
    machine_arn = resp["stateMachineArn"]

    try:
        click.echo(click.style('Running state machine...', fg='blue'))

        params = {k:v for (k, v) in param}

        params['topic_arn'] = topic_arn

        resp = client.start_execution(stateMachineArn=machine_arn, input=json.dumps(params))
        _sfn_waiter(resp['executionArn'])
        click.echo(click.style('State machine ran successfully.', fg='green'))
    finally:
        click.echo(click.style('Deleting state machine...', fg='blue'))
        client.delete_state_machine(stateMachineArn=machine_arn)


# class APIRoot(object): #pylint:disable=R0903
#     """ API root command """
#     def __init__(self, endpoint=None, account=None):
#         self.endpoint = endpoint
#         self.account = account

# @cli.group('sink')
# @click.option('--endpoint', default='https://api.drench.io/v1')
# @click.option('--account', default='global', help='Your drench api account id.')
# @click.pass_context
# def sink(ctx, endpoint, account):
#     """ Sink command group """
#     ctx.obj = APIRoot(endpoint, account)

# @sink.command('put', short_help='Create or update a sink with a workflow.')
# @click.option('--approval', default=False, help='Approval flag for sink.')
# @click.option('--name', '-n', help='Friendly name for the sink.')
# @click.argument('filename')
# @click.pass_obj
# def put_sink(api, name, filename, approval):
#     '''Create or update a sink with a workflow.'''
#     name = name or uuid.uuid4().hex
#
#     full_path = os.path.join(os.curdir, filename)
#     workflow = _load_workflow(full_path)
#
#     headers = {'x-drench-account': api.account}
#
#     # Try to find sink
#     try:
#         sinks = requests.get(f'{api.endpoint}/sinks', headers=headers).json()
#         sink_id = next(sink['source_id'] for sink in sinks if sink['name'] == name)
#
#         # Update sink
#         data = json.dumps({
#             'approval': approval,
#             'statemachine': workflow.as_dict()
#         })
#         resp = requests.put(f'{api.endpoint}/sinks/{sink_id}', headers=headers, data=data)
#         sink = resp.json()
#     except StopIteration:
#         # Create new sink
#         data = json.dumps({
#             'name': name,
#             'approval': approval,
#             'statemachine': workflow.as_dict()
#         })
#         resp = requests.post(f'{api.endpoint}/sinks', headers=headers, data=data)
#         sink = resp.json()
#
#     # Pretty Print Sink
#     click.echo(click.style(json.dumps(sink, indent=4), fg='blue'))

def main():
    """ main method """
    cli(obj={}) #pylint:disable=E1123,E1120

if __name__ == '__main__':
    main()
