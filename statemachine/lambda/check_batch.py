from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
from context import BotoContext

logger = logging.getLogger()

def handler(event, context):
    with BotoContext(service='batch', local=(context.aws_request_id == 'undefined')) as client:
        # Batch job parameters must be sent as {'batch':{}}
        if('batch' in event):
            batch = event['batch']
        else:
            raise BaseException("No batch job sent")

        jobId = batch['jobId']
        response = client.describe_jobs(jobs=[jobId])

        job = next(j for j in response['jobs'] if j['jobId'] == jobId)

        return job['status']
