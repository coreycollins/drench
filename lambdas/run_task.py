''' launch an aws task and report run id and output location '''
from os import sys, path
import boto3

sys.path.append(path.dirname(path.abspath(__file__)))
from sdk_utils import find_subs

RESULT_BUCKET = 's3://drench.io.results'

def handler(event, context): #pylint:disable=unused-argument
    ''' default lambda interface '''

    # raise KeyError if needed input missing
    task_type = event['next']['type']
    job_id = event['job_id']
    _ = event['principal_id']

    if 'result' not in event:
        event['result'] = {}

    # Substitute parameters
    event['next']['params'] = find_subs(dic=event['next']['params'],
                                        base=event,
                                        env={'{{JOB_PATH}}':f'{RESULT_BUCKET}/{job_id}'})

    #pylint:disable=line-too-long
    #consider setting AWS_DEFAULT_REGION env var for lambda?
    runner = {
        'glue': lambda p: boto3.client('glue', region_name='us-east-1').start_job_run(**p)['JobRunId'],
        'batch': lambda p: boto3.client('batch', region_name='us-east-1').submit_job(**p)['jobId'],
        'query':  lambda p: boto3.client('athena', region_name='us-east-1').start_query_execution(**p)['QueryExecutionId']
    }

    event['result']['job_id'] = runner[task_type](event['next']['params'])

    return event
