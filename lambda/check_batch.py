from __future__ import print_function
import json
import os
import logging
import boto3

logger = logging.getLogger()

def handler(event, context):
    client = boto3.client('batch', region_name='us-east-1')

    # Batch job parameters must be sent as {'batch':{}}
    if('batch' in event):
        batch = event['batch']
    else:
        raise BaseException("No batch job sent")

    jobId = batch['jobId']
    response = client.describe_jobs(jobs=[jobId])

    job = next(j for j in response['jobs'] if j['jobId'] == jobId)

    return job['status']
