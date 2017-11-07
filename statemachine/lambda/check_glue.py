from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
from context import BotoContext

logger = logging.getLogger()

def handler(event, context):
    with BotoContext(service='glue', local=(context.aws_request_id == 'undefined')) as client:
        # Batch job parameters must be sent as {'batch':{}}
        if('glue' in event):
            glue = event['glue']
        else:
            raise BaseException("No glue message sent")

        response = client.get_job_run(JobName=glue['JobName'], RunId=glue['runId'])

        return response['JobRun']['JobRunState']
