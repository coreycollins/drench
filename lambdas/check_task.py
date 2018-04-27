''' check the status of an aws task by run id and return it '''
import boto3

STATUS_INDEX = {
    'SUCCEEDED': 'pass',

    'FAILED': 'fail',
    'CANCELED':'fail',
    'TIMEOUT':'fail',
    'STOPPED': 'fail',

    'QUEUED': 'running',
    'RUNNING': 'running',
    'SUBMITTED': 'running',
    'PENDING': 'running',
    'RUNNABLE': 'running',
    'STARTING': 'running',
    'STOPPING': 'running'
}

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''

    def check_glue():
        '''get status for glue job'''
        client = boto3.client('glue', region_name='us-east-1')
        name = event['next']['params']['JobName']
        jid = event['result']['job_id']
        res = client.get_job_run(JobName=name, RunId=jid)
        return STATUS_INDEX[res['JobRun']['JobRunState']]

    def check_batch():
        '''get status for batch job'''
        client = boto3.client('batch', region_name='us-east-1')
        jid = event['result']['job_id']
        res = client.describe_jobs(jobs=[jid])
        job = next(j for j in res['jobs'] if j['jobId'] == jid)
        return STATUS_INDEX[job['status']]

    def check_query():
        '''get status for athena query'''
        client = boto3.client('athena', region_name='us-east-1')
        jid = event['result']['job_id']
        res = client.get_query_execution(QueryExecutionId=jid)
        return STATUS_INDEX[res['QueryExecution']['Status']['State']]

    runner = {
        'glue': check_glue,
        'batch': check_batch,
        'query': check_query
    }

    task_type = event['next']['type']
    return runner[task_type]()
