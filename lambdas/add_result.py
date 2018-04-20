'''update drench-api with stepp function step results'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    req_body = {
        'step': {
            'name': event['next']['name'],
            'out_path': event['next']['out_path'],
            'content_type': event['next']['content_type'],
            'status': event['result']['status']
        }
    }

    if 'report_url' in event['next']:
        req_body['step']['report_url'] = event['next']['report_url']

    req_payload = {
        'body': json.dumps(req_body),
        'requestContext': {
            'authorizer': {
                'principalId': event["principal_id"]
                }
            },
        'queryStringParameters': {},
        'headers': {},
        'httpMethod': 'PUT',
        'path': f'/jobs/{event["job_id"]}/steps'
    }

    client = boto3.client('lambda', region_name='us-east-1')

    invoke_res = client.invoke(
        FunctionName=f'arsa-drench-api:{event["api_version"]}',
        Payload=json.dumps(req_payload).encode()
    )

    res_payload = json.loads(invoke_res['Payload'].read())

    if res_payload['statusCode'] != 200:
        raise Exception(res_payload['body'])

    return event
