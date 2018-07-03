'''send status message through sns with channel config'''
import json
import boto3

SUBJECTS = {
    'running':'The step function has started running',
    'finished':'The step function has finished',
    'failed':'The step function has failed'
}

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    if 'sns_hook' not in event:
        return

    config = event['sns_hook']
    status = event['result']['status']

    payload = {
        'default': status,
        'lambda': json.dumps(event),
        'email': status.upper()
    }

    client.publish(
        TopicArn=config['topic_arn'],
        MessageStructure='json',
        Subject=SUBJECTS[status],
        Message=json.dumps(payload),
        MessageAttributes=config['attributes']
    )
