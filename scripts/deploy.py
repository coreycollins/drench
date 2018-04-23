#!/usr/bin/env python
''' deploy lambdas to AWS '''
import os
import shutil
import zipfile
import subprocess
import io
import re
import boto3

def main():
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

    lamba_client = boto3.client('lambda')

    # Run Task
    lamba_client.update_function_code(
        FunctionName='drench-sdk-run-task',
        ZipFile=buf.getvalue()
    )

    # Check Task
    lamba_client.update_function_code(
        FunctionName='drench-sdk-check-task',
        ZipFile=buf.getvalue()
    )

    # Add Result
    lamba_client.update_function_code(
        FunctionName='drench-sdk-add-result',
        ZipFile=buf.getvalue()
    )

    # Job Update
    lamba_client.update_function_code(
        FunctionName='drench-sdk-update-job',
        ZipFile=buf.getvalue()
    )

    # Send SNS on failure
    lamba_client.update_function_code(
        FunctionName='drench-sdk-send-sns',
        ZipFile=buf.getvalue()
    )

if __name__ == '__main__':
    main()
