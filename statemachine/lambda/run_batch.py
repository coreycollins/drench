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
