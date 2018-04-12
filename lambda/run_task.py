''' launch an aws task and report run id and output location '''
import boto3
import jsonpath_ng

RESULT_BUCKET = 's3://com.drench.results'

def handler(event, context): #pylint:disable=unused-argument
    ''' default lambda interface '''

    if 'result' in event:
        event['next']['in_path'] = event['result']['out_path']

    # $.next.in_path should be populated by above or user-input; raise KeyError if it is not
    _ = event['next']['in_path']

    # Construct output path by convention
    event['next']['out_path'] = f'{RESULT_BUCKET}/{event["job_id"]}/{event["next"]["name"]}/out'
    event['result']['out_path'] = event['next']['out_path']

    # Substitute parameters
    for key, val in event['next']['params'].iteritems():
        try:
            expr = jsonpath_ng.parse(val)
            event['next']['params'][key] = expr.find(event)[0].value
        except: #pylint:disable=bare-except
            pass

    #pylint:disable=line-too-long
    #consider setting AWS_DEFAULT_REGION env var for lambda?
    runner = {
        'glue': lambda p: boto3.client('glue', region_name='us-east-1').start_job_run(p)['JobRunId'],
        'batch': lambda p: boto3.client('batch', region_name='us-east-1').submit_job(p)['jobId'],
        'query':  lambda p: boto3.client('athena', region_name='us-east-1').start_query_execution(p)['QueryExecutionId']
    }

    event['result']['job_id'] = runner[event]['next']['type'](**event['next']['params'])

    return event
