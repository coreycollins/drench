import os, sys
import boto3
import pkg_resources

def get_resource(name):
    env = os.getenv("STATE_ENV") or "development"
    if (env != 'development'):
        client = boto3.client('lambda', region_name='us-east-1')
        lambda_name = '%s-%s' % (env,name)
        response = client.get_function_configuration(FunctionName=lambda_name)
        return response['FunctionArn']
    else:
        filename = name + '.py'
        resource_package = 'statemachine-lambda'  # Could be any module/package name
        resource_path = '/'.join(filename)  # Do not use os.path.join(), see below
        return pkg_resources.resource_filename(resource_package, resource_path)
