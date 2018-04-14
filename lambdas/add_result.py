'''update drench-api with stepp function step results'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    req_body = {
        'step': {
            'name': event['result']['name'],
            'out_path': event['result']['out_path'],
            'content_type': event['result']['content_type'],
            'status': event['result']['status']
        }
    }

    if event['result']['report_url']:
        req_body['step']['report_url'] = event['result']['report_url']

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
        FunctionName='arsa-drench-api:v1',
        Payload=json.dumps(req_payload).encode()
    )

    res_payload = json.loads(invoke_res['Payload'].read())

    if res_payload['statusCode'] != 200:
        raise Exception(res_payload['body'])

    return event
