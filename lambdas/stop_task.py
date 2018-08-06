''' check the status of an aws task by run id and return it '''
import boto3

def handler(event, _):
    '''default lambda interface'''

    def stop_glue(task_output):
        '''cancel glue job'''
        client = boto3.client('glue', region_name='us-east-1')
        res = client.batch_stop_job_run(JobName=task_output['next']['params']['JobName'],
                                        JobRunIds=[task_output['result']['job_id']])

        try:
            fail_job = next(j for j in res['Errors'] if j['JobRunId'] == task_output['result']['job_id'])
            raise Exception(fail_job['ErrorDetail']['ErrorMessage'])
        except StopIteration:
            pass

    def stop_batch(task_output):
        '''cancel batch job'''
        client = boto3.client('batch', region_name='us-east-1')
        client.terminate_job(jobId=task_output['result']['job_id'], reason='user cancelled')

    runner = {
        'glue': stop_glue,
        'batch': stop_batch,
    }

    res = boto3.client('stepfunctions', region_name='us-east-1').get_execution_history(
        executionArn=event['detail']['requestParameters']['executionArn'],
        reverseOrder=True)

    try:
        task_output = next(e['stateExitedEventDetails']['output'] for e in res['events'] if e['type'] == 'TaskStateExited')
    except StopIteration:
        return "OK"

    runner.get(task_output['next']['type'], lambda: None)(task_output)
    return "OK"
