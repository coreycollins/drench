import os, sys
import boto3
import json


def get_resource(name):
    env = os.getenv("STATE_ENV") or "development"
    if (env != 'development'):
        client = boto3.client('lambda', region_name='us-east-1')
        lambda_name = '%s-%s' % (env,name)
        response = client.get_function_configuration(FunctionName=lambda_name)
        return response['FunctionArn']
    else:
        return os.path.join(os.getcwd(),'lambda', name+'.py')
