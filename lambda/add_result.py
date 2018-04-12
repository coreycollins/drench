'''update drench-api with stepp function step results'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    payload = {
        'body': json.dumps(event['result']),
        'requestContext': {
            'authorizer': {
                # FIXME: below is hacky
                # alternative is to parse account id from context ARN
                'principalId': boto3.client('sts').get_caller_identity()['Account']
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
