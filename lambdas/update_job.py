'''update drench-api with the job state'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    payload = {
        'body': '{}',
        'requestContext': {
            'authorizer': {
                'principalId': event["account_id"]
                }
            },
        'queryStringParameters': {},
        'headers': {},
        'httpMethod': 'PUT',
        'path': f'/jobs/{event["job_id"]}/state/{event["result"]["status"]}'
    }

    client = boto3.client('lambda')

    client.invoke(
        FunctionName='arsa-drench-api:v1',
        Payload=json.dumps(payload).encode()
    )
