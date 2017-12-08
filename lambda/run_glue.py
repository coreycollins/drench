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

    # Substitute parameters
    if ('Arguments' in glue):
        for k,v in batch['Arguments'].iteritems():
            try:
                expr = jsonpath_ng.parse(v)
                batch['Arguments'][k] = expr.find(event)[0].value
            except:
                pass


    response = client.start_job_run(**glue)

    return response['JobRunId']
