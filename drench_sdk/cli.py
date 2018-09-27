''' SDK CLI '''
#!/usr/bin/env python

import os
import sys
import importlib
import time
import io
import zipfile
import tempfile
import subprocess
import shutil
import re
import json
import uuid
import boto3
import click
from botocore.exceptions import ClientError
import botocore.session

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
            res = client.get_execution_history(
                executionArn=execution_arn,
                maxResults=25
            )

            click.echo(json.dumps(res, indent=4, default=str))
            raise click.ClickException('Error running statemachine')

        time.sleep(1)

def _resource_not_found(error):
    code = error.response.get('Error', {}).get('Code', 'Unknown')
    return code == 'ResourceNotFoundException'

def _entity_not_found(error):
    code = error.response.get('Error', {}).get('Code', 'Unknown')
    return code == 'NoSuchEntity'

def _cannot_assume(error):
    message = error.response.get('Error', {}).get('Message', 'Unknown')
    return message == 'The role defined for the function cannot be assumed by Lambda.'


class PublishCommand(object):
    """ Command class to publish a lambda package to AWS """

    def __init__(self, function_name, role_name, region):
        self.function_name = function_name
        self.role_name = role_name
        self.region = region

        # Check for credentials
        self.session = boto3.Session(region_name=region)
        if self.session.get_credentials() is None:
            raise click.ClickException('No AWS credentials were found.')

    def publish(self):
        """ publish the lambda package """
        build_path = tempfile.mkdtemp()
        buf = self._build(build_path)

        # Create IAM Execution Role
        role_arn = self._setup_role()

        # Push lambda function
        function_arn = self._push_lambda(role_arn, buf)

        return {
            'function_name': self.function_name,
            'function_arn': function_arn,
            'role_name': self.role_name,
            'role_arn':role_arn,
            'region': self.region
        }

    def destroy(self):
        """ Destroy all resources published by drench """
        # Destroy lambda function
        try:
            lamba_client = self.session.client('lambda')
            lamba_client.delete_function(FunctionName=self.function_name)
        except ClientError as error:
            if not _resource_not_found(error):
                raise error

        # Destroy role
        try:
            iam_client = self.session.client('iam')
            iam_client.delete_role_policy(RoleName=self.role_name, PolicyName='drench-lambda-permissions')
            iam_client.delete_role(RoleName=self.role_name)
        except ClientError as error:
            if not _resource_not_found(error):
                raise error


    def _build(self, tempdir):
        """ build the package """
        click.secho('Building package...', fg='green')
        build_path = os.path.join(tempdir, 'package')

        # Find package path
        module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lambdas')
        shutil.copytree(module_path, build_path)

        fnull = open(os.devnull, 'w')
        subprocess.check_call([
            'pip',
            'install',
            'jsonpath_ng',
            '-t',
            build_path
        ], stdout=fnull)

        # zip together for distribution
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as myzip:
            for base, _, files in os.walk(build_path, followlinks=True):
                for file in files:
                    if not re.match(r'.*\.pyc', file):
                        path = os.path.join(base, file)
                        myzip.write(path, path.replace(build_path + '/', ''))

        return buf

    def _push_lambda(self, role_arn, buf):
        click.secho('Uploading {} package...'.format(self.function_name), fg='green')

        lamba_client = self.session.client('lambda')
        try:
            resp = lamba_client.update_function_code(
                FunctionName=self.function_name,
                ZipFile=buf.getvalue()
            )
            function_arn = resp['FunctionArn']
        except ClientError as error:
            if _resource_not_found(error):
                click.secho('Creating new lambda function...', fg='yellow')
                delay = retry = 1
                while retry < 20:
                    try:
                        resp = lamba_client.create_function(
                            FunctionName=self.function_name,
                            Runtime='python3.6',
                            Role=role_arn,
                            Handler='main.handler',
                            Code={
                                'ZipFile': buf.getvalue()
                            }
                        )
                        function_arn = resp['FunctionArn']
                        break
                    except ClientError as assume_error:
                        if _cannot_assume(assume_error):
                            time.sleep(delay)
                            delay = delay*2
                            retry += 1
                        else:
                            raise assume_error
            else:
                raise error

        return function_arn

    def _setup_role(self):
         # Create lambda execution role
        iam_client = self.session.client('iam')
        try:
            resp = iam_client.get_role(RoleName=self.role_name)
            role_arn = resp['Role']['Arn']
        except ClientError as error:
            if _entity_not_found(error):
                click.secho('Creating new lambda role...', fg='yellow')
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }

                resp = iam_client.create_role(
                    RoleName=self.role_name,
                    AssumeRolePolicyDocument=json.dumps(policy),
                    Description='Drench lambda execution role'
                )
                role_arn = resp['Role']['Arn']
            else:
                raise error

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ['logs:*', 'glue:*', 'batch:*', "lambda:*", "states:*"],
                    "Resource": "*"
                }
            ]
        }

        # Attach role policy for lambda function
        click.secho('Setting permissions to execution role...', fg='green')
        iam_client.put_role_policy(
            RoleName=self.role_name,
            PolicyName='drench-lambda-permissions',
            PolicyDocument=json.dumps(policy)
        )

        return role_arn


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

@cli.command('publish', short_help='Publish Drench resources.')
@click.option('--config_path', '-c', default=os.curdir)
@click.option('--function_name', default='drench-lambda')
@click.option('--role_name', default='drench-lambda-role')
@click.option('--region', default='us-east-1')
def publish(config_path, function_name, role_name, region):
    """ Publish the resources needed by Drench. """
    config_file = os.path.join(config_path, 'drench.json')

    cmd = PublishCommand(function_name, role_name, region)
    resources = cmd.publish()

    # Write config file
    with open(config_file, 'w') as outfile:
        json.dump(resources, outfile)

@cli.command('destroy', short_help='Destroy Drench resources.')
@click.option('--config_path', '-c', default=os.curdir)
def destroy(config_path):
    """ Publish the resources needed by Drench. """
    config_file = os.path.join(config_path, 'drench.json')

    if not os.path.isfile(config_file):
        raise click.ClickException('The Drench resources json file cannot be found.')

    resources = json.load(open(config_file, 'r'))

    cmd = PublishCommand(resources['function_name'], resources['role_name'], resources['region'])
    cmd.destroy()

    os.remove(config_file)

def main():
    """ main method """
    cli(obj={}) #pylint:disable=E1123,E1120

if __name__ == '__main__':
    main()
