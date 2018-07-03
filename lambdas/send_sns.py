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

    topic_arn = event['topic_arn']

    message_attrs = {'source':{'DataType':'String', 'StringValue':'drench_sdk'}}

    # Principal ID can be sent through to allow for filtering on backend
    if 'principal_id' in event:
        message_attrs['principal_id'] = {
            'DataType':'String',
            'StringValue':str(event['principal_id'])
        }

    status = event['result']['status']

    payload = {
        'default': status,
        'lambda': json.dumps(event),
        'email': status.upper()
    }

    client.publish(
        TopicArn=topic_arn,
        MessageStructure='json',
        Subject=SUBJECTS[status],
        Message=json.dumps(payload),
        MessageAttributes=message_attrs
    )
