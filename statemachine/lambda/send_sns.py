from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
from context import BotoContext

logger = logging.getLogger()

def handler(event, context):
    with BotoContext(service='sns', local=(context.aws_request_id == 'undefined')) as client:

        if('sns' in event):
            sns = event['sns']
        else:
            raise BaseException("No sns message sent")

        process_id = event['id']

        client.publish(
            TopicArn=sns['arn'],
            Message=sns['message'],
            Subject=sns['subject']
        )
