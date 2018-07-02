'''report when sdk -> api communication fails'''
import json
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    if 'topic_arn' not in event:
        raise Exception('Topic Arn not found')

    raw_data = json.dumps(event)
    message = {
        'default': raw_data,
        'drench': raw_data
    }

    client.publish(
        TopicArn=event['topic_arn'],
        MessageStructure='json',
        Message=json.dumps(message)
    )
