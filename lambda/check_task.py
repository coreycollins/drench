''' check the status of an aws task by run id and return it '''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''

    client = boto3.client('glue', region_name='us-east-1')
    response = client.get_job_run(JobName=event['next']['params']['JobName'], RunId=event['result']['runId'])

    return response['JobRun']['JobRunState']
