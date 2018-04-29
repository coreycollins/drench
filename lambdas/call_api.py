'''update drench-api with stepp function step results'''
import json
from os import sys, path
import boto3

sys.path.append(path.dirname(path.abspath(__file__)))
from sdk_utils import find_subs, build_path

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''
    # Substitute parameters
    if 'body' in event['api_call']:
        body = find_subs(event['api_call']['body'], event)
    else:
        body = ''

    req_payload = {
        'body': json.dumps(body),
        'requestContext': {
            'identity': {
                'user': 'internal' # This must be set for the API to grant access
            }
        },
        'queryStringParameters': {},
        'headers': {
            'x-drench-account': event["principal_id"]
        },
        'httpMethod': event['api_call']['method'],
        'path': build_path(event['api_call']['path'], event)
    }

    client = boto3.client('lambda', region_name='us-east-1')

    invoke_res = client.invoke(
        FunctionName=f'arsa-drench-api:{event["api_version"]}',
        Payload=json.dumps(req_payload).encode()
    )

    res_payload = json.loads(invoke_res['Payload'].read())

    if res_payload['statusCode'] != 200:
        raise Exception(res_payload['body'])

    return res_payload['body']
