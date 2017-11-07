from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
from context import BotoContext

logger = logging.getLogger()

def handler(event, context):
    with BotoContext(service='glue', local=(context.aws_request_id == 'undefined')) as client:

        if('glue' in event):
            glue = event['glue']
        else:
            raise BaseException("No glue message sent")

        process_id = event['process_id']

        client.start_job_run(**glue)
