""" tasks """
import boto3
from .exceptions import TaskException

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

class Task(object):
    """ Base Task class for different implementations of an asynchronous task on AWS """

    def start(self, params):
        """
        Start a instance of this taskself.
        @returns: Indentifiers for the task which is a dictionary of key/values
        """
        pass

    def stop(self, identifiers):
        """ Stop a instance of this task given the identifiers"""
        pass

    def check(self, identifiers):
        """
        Check for the status of the task given the indentifiers
        @returns: status
        """
        pass


class GlueTask(Task):
    """ Implements calling AWS Glue """
    def start(self, params):
        client = boto3.client('glue')
        res = client.start_job_run(**params)['JobRunId']

        return {
            'JobName': params['JobName'],
            'RunId': res['JobRunId']
        }

    def check(self, identifiers):
        client = boto3.client('glue')
        res = client.get_job_run(**identifiers)
        return STATUS_INDEX[res['JobRun']['JobRunState']]

    def stop(self, identifiers):
        client = boto3.client('glue')
        client.batch_stop_job_run(JobName=identifiers['JobName'], JobRunIds=[identifiers['RunId']])

class BatchTask(Task):
    """ Implements calling AWS Batch """
    def start(self, params):
        client = boto3.client('batch')
        res = client.submit_job(**params)
        return {'JobId': res['jobId']}

    def check(self, identifiers):
        client = boto3.client('batch')
        job_id = identifiers['JobId']
        res = client.describe_jobs(jobs=[job_id])

        try:
            job = next(j for j in res['jobs'] if j['jobId'] == job_id)
        except StopIteration:
            raise TaskException("Unable to find batch job")

        return STATUS_INDEX[job['status']]

    def stop(self, identifiers):
        client = boto3.client('batch')
        client.terminate_job(jobId=identifiers['JobId'], reason='user cancelled')
