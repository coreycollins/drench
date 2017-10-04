import os, sys
import boto3
import json

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Resources(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.configurations = None
        self.env = os.getenv("STATE_ENV") or "development"

    def get(self, name):
        if (self.env != 'development'):
            client = boto3.client('lambda', region_name='us-east-1')
            lambda_name = '%s-%s' % (env,name)
            response = client.get_function_configuration(FunctionName=lambda_name)
            return response['FunctionArn']
        else:
            return os.path.join(os.getcwd(),'lambda', name+'.py')

    def __get_configutation(self):
        """get configurations from s3 path"""
        client = boto3.client('s3', region_name='us-east-1')
        config_s3_object = client.get_object(Bucket='infra.compass.com',
                                             Key='%s/output.json' % self.env)
        config_object = json.loads(config_s3_object['Body'].read())
        return config_object
