'''send status message through sns with channel config'''
import json
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    topic_arn = event['topic_arn']

    payload = {
        'type': 'sfn',
        'state': event
    }

    message = {
        'default': event['result']['status'],
        'lambda': json.dumps(payload)
    }

    client.publish(
        TopicArn=topic_arn,
        MessageStructure='json',
        Message=json.dumps(message)
    )
