'''update drench-api with the job state'''
import json
import boto3

SUCCESS_INDICATOR = 'pass'
SUCCESS_STATE = 'finish'
FAILURE_STATE = 'failed'

def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''
    try:
        if event["result"]["status"] == SUCCESS_INDICATOR:
            state = SUCCESS_STATE
        else:
            state = FAILURE_STATE
    except KeyError:
        state = FAILURE_STATE

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
        FunctionName=f'arsa-drench-api:{event["api_version"]}',
        Payload=json.dumps(payload).encode()
    )

    body = json.loads(res['Payload'].read())

    if body['statusCode'] != 200:
        raise Exception(body['body'])

    return event
