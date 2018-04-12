'''update drench-api with stepp function step results'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    payload = {
        'body': json.dumps(event['result']),
        'requestContext': {
            'authorizer': {
                'principalId': 1234 #FIXME hard code?
                }
            },
        'queryStringParameters': {},
        'headers': {},
        'httpMethod': 'PUT',
        'path': '/jobs/{event["job_id"]}/steps'
    }

    client = boto3.client('lambda')

    client.invoke(
        FunctionName='arsa-drench-api:v1',
        Payload=json.dumps(payload).encode()
    )
