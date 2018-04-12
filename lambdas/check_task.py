''' check the status of an aws task by run id and return it '''
import boto3

PASS = 'pass'
FAIL = 'fail'

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''

    def check_glue():
        '''get status for glue job'''
        client = boto3.client('glue', region_name='us-east-1')
        name = event['next']['params']['JobName']
        jid = event['result']['job_id']
        res = client.get_job_run(JobName=name, RunId=jid)
        return PASS if res['JobRun']['JobRunState'] == 'SUCCEEDED' else FAIL

    def check_batch():
        '''get status for batch job'''
        client = boto3.client('batch', region_name='us-east-1')
        jid = event['result']['job_id']
        res = client.describe_jobs(jobs=[jid])
        job = next(j for j in res['jobs'] if j['jobId'] == jid)
        return PASS if job['status'] == 'SUCCEEDED' else FAIL

    def check_query():
        '''get status for athena query'''
        client = boto3.client('athena', region_name='us-east-1')
        jid = event['result']['job_id']
        res = client.get_query_execution(QueryExecutionId=jid)
        return PASS if res['QueryExecution']['Status']['State'] == 'SUCCEEDED' else FAIL

    runner = {
        'glue': check_glue,
        'batch': check_batch,
        'query': check_query
    }

    task_type = event['next']['type']
    return {
        'name': event['next']['name'],
        'out_path': event['next']['out_path'],
        'content_type': event['next']['content_type'],
        'report_url': event['next']['report_url'],
        'status': runner[task_type]()
    }
