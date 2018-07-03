'''send status message through sns with channel config'''
import json
import boto3

SUBJECTS = {
    'running': 'The job has started running',
    'finished': 'The job has finished',
    'failed': 'The job has failed'
}

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    topic_arn = event['topic_arn']
    status = event['result']['status']

    client.publish(
        TopicArn=topic_arn,
        Subject=SUBJECTS[status],
        Message=json.dumps(event, indent=4),
        MessageAttributes={
            'message_type': {'DataType':'String', 'StringValue':'sfn'}
        }
    )
