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
        self.env = os.getenv("STEP_ENV") or "development"

    def get(self, name):
        if (self.configurations is None):
            self.configurations = self.__get_configutation()
        return self.configurations[name]['value']

    def __get_configutation(self):
        """get configurations from s3 path"""
        client = boto3.client('s3', region_name='us-east-1')
        config_s3_object = client.get_object(Bucket='infra.compass.com',
                                             Key='%s/output.json' % self.env)
        config_object = json.loads(config_s3_object['Body'].read())
        return config_object
