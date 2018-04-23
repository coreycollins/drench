'''report when sdk -> api communication fails'''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    client.publish(
        TopicArn=event['sns']['topic_arn'],
        Message=event['err_info'],
        Subject=event['sns']['subject']
    )
