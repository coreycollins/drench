''' launch an aws task and report run id and output location '''
import boto3
import jsonpath_ng

RESULT_BUCKET = 's3://com.drench.results'

def handler(event, context): #pylint:disable=unused-argument
    ''' default lambda interface '''

    if 'result' in event:
        event['next']['in_path'] = event['result']['out_path']

    # Construct output path by convention
    event['next']['out_path'] = f'{RESULT_BUCKET}/{event["job_id"]}/{event["next"]["name"]}/out'

    # Substitute parameters
    for key, val in event['next']['params'].iteritems():
        try:
            expr = jsonpath_ng.parse(val)
            event['next']['params'][key] = expr.find(event)[0].value
        except: #pylint:disable=bare-except
            pass

    #FIXME case-switch support different resources (batch, athena, etc)
    client = boto3.client('glue', region_name='us-east-1')
    response = client.start_job_run(**event['next']['params'])

    event['result'] = {
        'run_id': response['JobRunId'],
        'out_path': event['next']['out_path']
    }

    return event
