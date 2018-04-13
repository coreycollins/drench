'''update drench-api with stepp function step results'''
import json
import boto3

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    body = {
        'step': {
            'name': event['result']['name'],
            'out_path': event['result']['out_path'],
            'content_type': event['result']['content_type'],
            'status': event['result']['status']
        }
    }

    if event['result']['report_url']:
        body['step']['report_url'] = event['result']['report_url']

    payload = {
        'body': json.dumps(body),
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

    res = client.invoke(
        FunctionName='arsa-drench-api:v1',
        Payload=json.dumps(payload).encode()
    )

    body = json.loads(res['Payload'].read())

    if body['statusCode'] != 200:
        raise Exception(body['body'])

    return event
