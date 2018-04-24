#!/usr/bin/env python
''' deploy lambdas to AWS '''
import os
import shutil
import zipfile
import subprocess
import io
import re
from sys import argv
import boto3

DRENCH_SDK_LAMBDAS = ['run-task', 'check-task', 'add-result', 'update-job', 'send-sns']
DEPLOY_ALIAS = argv[1]

def main(): #pylint:disable=too-many-locals
    """ main method """
    lambda_path = os.path.join(os.curdir, 'lambdas')
    build_path = os.path.join(os.curdir, '.build')

    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)

    # install packages
    fnull = open(os.devnull, 'w')
    subprocess.check_call([
        'pip',
        'install',
        '-r',
        os.path.join(lambda_path, 'requirements.txt'),
        '-t',
        build_path
    ], stdout=fnull)

    files = [f for f in os.listdir(lambda_path) if re.match(r'^.*\.py$', f)]
    for f in files: #pylint:disable=invalid-name
        src = os.path.join(lambda_path, f)
        dst = os.path.join(build_path, f)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.pyc'))
        elif os.path.isfile(src):
            shutil.copy(src, dst)


    # zip together for distribution
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as myzip:
        for base, _, files in os.walk(build_path, followlinks=True):
            for file in files:
                path = os.path.join(base, file)
                myzip.write(path, path.replace(build_path + '/', ''))

    lambda_client = boto3.client('lambda')

    for drench_lambda in DRENCH_SDK_LAMBDAS:
        func_name = f'drench-sdk-{drench_lambda}'
        update_resp = lambda_client.update_function_code(
            FunctionName=func_name,
            ZipFile=buf.getvalue(),
            Publish=True
        )

        try:
            lambda_client.get_alias( #check that lambda exists
                FunctionName=func_name,
                Name=DEPLOY_ALIAS
            )
            lambda_client.update_alias( #then update it
                FunctionName=func_name,
                Name=DEPLOY_ALIAS,
                FunctionVersion=update_resp['Version']
            )
        except lambda_client.exceptions.ResourceNotFoundException:
            lambda_client.create_alias( #othwerise create it
                FunctionName=func_name,
                Name=DEPLOY_ALIAS,
                FunctionVersion=update_resp['Version']
            )

if __name__ == '__main__':
    main()
