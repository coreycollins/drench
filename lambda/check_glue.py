from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
import boto3

logger = logging.getLogger()

def handler(event, context):
    client = boto3.client('glue', region_name='us-east-1')

    # Glue job parameters must be sent as {'glue':{}}
    if('glue' in event):
        glue = event['glue']
    else:
        raise BaseException("No glue message sent")

    response = client.get_job_run(JobName=glue['JobName'], RunId=glue['runId'])

    return response['JobRun']['JobRunState']
