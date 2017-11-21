from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
import boto3

logger = logging.getLogger()

def handler(event, context):
    client = boto3.client('glue', region_name='us-east-1')

    if('glue' in event):
        glue = event['glue']
    else:
        raise BaseException("No glue message sent")

    process_id = event['process_id']

    response = client.start_job_run(**glue)

    return response['JobRunId']
