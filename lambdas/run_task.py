''' launch an aws task and report run id and output location '''
import boto3
from .sdk_util import find_subs

RESULT_BUCKET = 's3://com.drench.results'

def handler(event, context): #pylint:disable=unused-argument
    ''' default lambda interface '''

    if 'result' in event:
        event['next']['in_path'] = event['result']['out_path']

    # raise KeyError if needed input missing
    task_type = event['next']['type']
    if task_type != 'query':
        _ = event['next']['in_path']

    _ = event['job_id']
    _ = event['principal_id']

    if 'result' not in event:
        event['result'] = {}

    # Construct output path by convention
    event['next']['out_path'] = f'{RESULT_BUCKET}/{event["job_id"]}/{event["next"]["name"]}/out'
    event['result']['out_path'] = event['next']['out_path']

    # Substitute parameters
    event['next']['params'] = find_subs(event['next']['params'], event)

    #pylint:disable=line-too-long
    #consider setting AWS_DEFAULT_REGION env var for lambda?
    runner = {
        'glue': lambda p: boto3.client('glue', region_name='us-east-1').start_job_run(**p)['JobRunId'],
        'batch': lambda p: boto3.client('batch', region_name='us-east-1').submit_job(**p)['jobId'],
        'query':  lambda p: boto3.client('athena', region_name='us-east-1').start_query_execution(**p)['QueryExecutionId']
    }

    event['result']['job_id'] = runner[task_type](event['next']['params'])

    return event
