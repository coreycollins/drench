from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
import boto3

logger = logging.getLogger()

def handler(event, context):
    client = boto3.client('batch', region_name='us-east-1')

    # Batch job parameters must be sent as {'batch':{}}
    if('batch' in event):
        batch = event['batch']
    else:
        raise BaseException("No batch job sent")

    # Substitute parameters
    if ('parameters' in batch):
        for k,v in batch['parameters'].iteritems():
            try:
                expr = jsonpath_ng.parse(v)
                batch['parameters'][k] = expr.find(event)[0].value
            except:
                pass


    response = client.submit_job(**batch)

    return response['jobId']
