#!/usr/bin/env python
''' deploy lambdas to AWS '''
import os
import shutil
import zipfile
import subprocess
import json
import io
import re
from sys import argv
import boto3

DRENCH_SDK_LAMBDAS = ['run-task', 'check-task', 'call-api', 'send-sns']
DEPLOY_ALIAS = argv[1]

def _setup_role(role_name):
     # Create lambda execution role
    iam_client = boto3.client('iam')
    try:
        resp = iam_client.get_role(RoleName=role_name)
        role_arn = resp['Role']['Arn']
        print(f'fetched lambda role {role_arn}')
    except iam_client.exceptions.NoSuchEntityException:
        print(f'creating lambda role {role_name}')

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }
            ]
        }

        resp = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(policy),
            Description='Drench SDK lambda execution role'
        )

        role_arn = resp['Role']['Arn']

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:*"
                    ],
                    "Resource": [
                        "arn:aws:logs:*:*:*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "sqs:*",
                        "batch:*",
                        "sns:*",
                        "s3:*",
                        "states:*",
                        "athena:*",
                        "glue:*",
                        "lambda:*"
                    ],
                    "Resource": "*"
                }
            ]
        }

        # Attach role policy for lambda function
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='drench-lambda-permissions',
            PolicyDocument=json.dumps(policy)
        )

    return role_arn

def main(): #pylint:disable=too-many-locals
    """ main method """
    lambda_path = os.path.join(os.curdir, 'lambdas')
    build_path = os.path.join(os.curdir, '.build')

    print(f'creating build directory {build_path}')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)

    # install packages
    print('installing deps from requirements.txt')
    fnull = open(os.devnull, 'w')
    subprocess.check_call([
        'pip',
        'install',
        '-r',
        os.path.join(lambda_path, 'requirements.txt'),
        '-t',
        build_path
    ], stdout=fnull)

    print(f'compying functions from {lambda_path} to {build_path}')
    files = [f for f in os.listdir(lambda_path) if re.match(r'^.*\.py$', f)]
    for f in files: #pylint:disable=invalid-name
        src = os.path.join(lambda_path, f)
        dst = os.path.join(build_path, f)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.pyc'))
        elif os.path.isfile(src):
            shutil.copy(src, dst)


    # zip together for distribution
    print(f'zipping all files in {build_path}')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as myzip:
        for base, _, files in os.walk(build_path, followlinks=True):
            for file in files:
                path = os.path.join(base, file)
                myzip.write(path, path.replace(build_path + '/', ''))

    lambda_client = boto3.client('lambda')
    role_arn = _setup_role('drench-sdk-lambda-exec-role')

    for drench_lambda in DRENCH_SDK_LAMBDAS:
        func_name = f'drench-sdk-{drench_lambda}'
        handler = f'{drench_lambda.replace("-","_")}.handler'

        try:
            resp = lambda_client.update_function_code(
                FunctionName=func_name,
                ZipFile=buf.getvalue(),
                Publish=True
            )
            print(f'updated function {func_name}')
        except lambda_client.exceptions.ResourceNotFoundException:
            resp = lambda_client.create_function(
                FunctionName=func_name,
                Runtime='python3.6',
                Role=role_arn,
                Handler=handler,
                Code={
                    'ZipFile': buf.getvalue()
                },
                Publish=True
            )
            print(f'created function {func_name}')

        try:
            lambda_client.update_alias(
                FunctionName=func_name,
                Name=DEPLOY_ALIAS,
                FunctionVersion=resp['Version']
            )
            print(f'updated alias {func_name}:{DEPLOY_ALIAS}')
        except lambda_client.exceptions.ResourceNotFoundException:
            lambda_client.create_alias(
                FunctionName=func_name,
                Name=DEPLOY_ALIAS,
                FunctionVersion=resp['Version']
            )
            print(f'created alias {func_name}:{DEPLOY_ALIAS}')

if __name__ == '__main__':
    main()
