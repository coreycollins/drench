''' check the status of an aws task by run id and return it '''
import boto3

def handler(event, context): #pylint:disable=unused-argument
    '''default lambda interface'''

    #FIXME case-switch support different resources (batch, athena, etc)
    client = boto3.client('glue', region_name='us-east-1')
    response = client.get_job_run(JobName=event['next']['params']['JobName'], RunId=event['result']['runId'])
    status = response['JobRun']['JobRunState']

    return {
        'name': event['next']['name'],
        'out_path': event['next']['out_path'],
        'content_type': event['next']['content_type'],
        'report': event['next']['report'],
        'status': status
    }
