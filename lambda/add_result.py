'''update drench-api with stepp function step results'''
import json
import jsonpath_ng
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    expr = jsonpath_ng.parse('$.next.account_id')
    account_id = expr.find(event)[0].value

    payload = {
        'body': json.dumps(event['result']),
        'requestContext': {
            'authorizer': {
                'principalId': account_id
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
