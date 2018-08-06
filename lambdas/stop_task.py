''' check the status of an aws task by run id and return it '''
import boto3

def handler(event, _):
    '''default lambda interface'''

    def stop_glue(task_output):
        '''cancel glue job'''
        client = boto3.client('glue', region_name='us-east-1')
        res = client.batch_stop_job_run(JobName=task_output['next']['JobName'],
                                        JobRunIds=[task_output['result']['job_id']])

        fail_job = next(j for j in res['Errors'] if j['JobRunId'] == task_output['result']['job_id'])
        if fail_job:
            raise Exception(fail_job['ErrorDetail']['ErrorMessage'])

    def stop_batch(task_output):
        '''cancel batch job'''
        client = boto3.client('batch', region_name='us-east-1')
        client.terminate_job(jobId=task_output['result']['job_id'])

    runner = {
        'glue': stop_glue,
        'batch': stop_batch,
    }

    res = boto3.client('sfn', region_name='us-east-1').get_execution_history(
        executionArn=event['detail']['requestParameters']['executionArn'],
        reverseOrder=True)

    try:
        task_output = next(e['output'] for e in res['events'] if e['type'] == 'TaskStateExited')
        try:
            runner[task_output['next']['type']](task_output)
            return None
        except KeyError:
            return None
    except StopIteration:
        return None
