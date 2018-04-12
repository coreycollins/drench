''' check the status of an aws task by run id and return it '''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''

    def check_glue(**kwargs):
        '''get status for glue job'''
        client = boto3.client('glue', region_name='us-east-1')
        name = kwargs['job_name']
        jid = kwargs['job_id']
        return client.get_job_run(JobName=name, RunId=jid)['JobRun']['JobRunState']

    def check_batch(**kwargs):
        '''get status for batch job'''
        client = boto3.client('batch', region_name='us-east-1')
        response = client.describe_jobs(jobs=[kwargs['job_id']])
        job = next(j for j in response['jobs'] if j['jobId'] == kwargs['job_id'])
        return job['status']

    def check_query(**kwargs):
        '''get status for athena query'''
        client = boto3.client('athena', region_name='us-east-1')
        response = client.get_query_execution(QueryExecutionId=kwargs['job_id'])
        return response['QueryExecution']['Status']['State']

    runner = {
        'glue': check_glue,
        'batch': check_batch,
        'query': check_query
    }


    check_params = {
        'job_id': event['result']['job_id']
    }

    if event['next']['type'] == 'glue':
        check_params['job_name'] = event['next']['params']['JobName']

    return {
        'name': event['next']['name'],
        'out_path': event['next']['out_path'],
        'content_type': event['next']['content_type'],
        'report': event['next']['report'],
        'status': runner['event']['next']['type'](check_params)
    }
