'''send status message through sns with channel config'''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    topic_arn = event['topic_arn']

    #FIXME This is a direct dependcy from the API and needs to be fixed
    job_id = event['job_id']
    account_id = event['account_id']

    client.publish(
        TopicArn=topic_arn,
        Message=event['result']['status'],
        MessageAttributes={
            'message_type': {'DataType':'String', 'StringValue':'sfn'},
            'account_id': {'DataType':'String', 'StringValue': str(account_id)},
            'job_id': {'DataType':'String', 'StringValue': str(job_id)}
        }
    )
