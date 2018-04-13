'''update drench-api with the job state'''
import json
import boto3

JOB_STATE = {
    'start': 'running',
    'pass': 'finished',
    'fail': 'failed'
}

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    state = JOB_STATE[event["result"]["status"]]
    payload = {
        'body': '{}',
        'requestContext': {
            'authorizer': {
                'principalId': event["principal_id"]
                }
            },
        'queryStringParameters': {},
        'headers': {},
        'httpMethod': 'PUT',
        'path': f'/jobs/{event["job_id"]}/state/{state}'
    }

    client = boto3.client('lambda')

    res = client.invoke(
        FunctionName='arsa-drench-api:v1',
        Payload=json.dumps(payload).encode()
    )

    if res['StatusCode'] != 200:
        raise Exception(res['FunctionError'])

    return event
