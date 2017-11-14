from __future__ import print_function
import json
import os
import logging
import jsonpath_ng
import boto3

logger = logging.getLogger()

def handler(event, context):
    client = boto3.client('sns', region_name='us-east-1')

    if('sns' in event):
        sns = event['sns']
    else:
        raise BaseException("No sns message sent")

    client.publish(
        TopicArn=sns['arn'],
        Message=sns['message'],
        Subject=sns['subject']
    )
