'''update drench-api with stepp function step results'''
import json
import boto3
from .sdk_util import build_path, find_subs

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''
    # Substitute parameters
    event['api_call']['body'] = find_subs(event['api_call']['body'], event)

    req_payload = {
        'body': json.dumps(event['api_call']['body']),
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
