'''report when sdk -> api communication fails'''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''
    client = boto3.client('sns', region_name='us-east-1')

    client.publish(
        TopicArn=event['fail_sns_topic'],
        Message=event['err_info'],
        Subject='Step Function Communication failure on job id: {event["job_id"]}'
    )
