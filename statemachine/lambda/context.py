import boto3
import subprocess
import sys, os
import urlparse
import string
import uuid

class BotoContext():
    def __init__(self, service, local=False):
        self.service = service
        self.mock = local

    def __enter__(self):
        if(self.mock):
            if (self.service == 'batch'):
                client = MockBatch()
            elif (self.service == 'sns'):
                client = MockSNS()
            elif (self.service == 'glue'):
                client = MockGlue()
            else:
                raise BaseException("Service is not implemented locally.")
        else:
            client = boto3.client(self.service, region_name='us-east-1')
        return client

    def __exit__(self, *args):
        pass

class MockSNS(object):

    def publish(self, **kwargs):
        print("Sent SNS Message: {}".format(kwargs))

class MockGlue(object):

    def get_job_run(self, **kwargs):
        return {'JobRun':{'JobRunState':'SUCCEEDED'}}
        
    def start_job_run(self, **kwargs):
        client = boto3.client('glue', region_name='us-east-1')

        if ('Arguments' in kwargs and 'scriptLocation' in kwargs['Arguments']):
            scriptLocation = kwargs['Arguments']['scriptLocation']
        else:
            res = client.get_job(JobName=kwargs['JobName'])
            scriptLocation = res['Job']['Command']['ScriptLocation']

        input_path = urlparse.urlparse(scriptLocation)

        # If script is on S3, download it
        if (input_path.scheme == 's3'):
            s3 = boto3.client('s3', region_name='us-east-1')
            bucket = input_path.netloc
            key = string.lstrip(input_path.path,'/')
            scriptLocation = '/tmp/%s.py' % uuid.uuid4().hex

            s3.download_file(Bucket=bucket, Key=key, Filename=scriptLocation)


        subprocess.check_call(['python', scriptLocation], env=os.environ)

class MockBatch(object):

    def describe_jobs(self, **kwargs):
        jobs = kwargs['jobs']
        return {'jobs': map(lambda x: {'jobName':'MockJob', 'jobId':x, 'status':'SUCCEEDED'}, jobs)}

    def submit_job(self, **kwargs):
        # We need this to gather the job definition
        client = boto3.client('batch', region_name='us-east-1')

        # Get the job definition from AWS
        result = client.describe_job_definitions(jobDefinitionName=kwargs['jobDefinition'], status='ACTIVE')
        job = result["jobDefinitions"][0]

        volumes = []
        parameters = kwargs['parameters'] or {}
        overrides  = kwargs['containerOverrides'] or []

        try:
            for vol in job['containerProperties']['volumes']:
                # Get corresponding mount pount
                mp = next(mp for mp in job['containerProperties']['mountPoints'] if mp['sourceVolume'] == vol['name'])

                # Create volume container
                subprocess.check_call([
                        'docker',
                        'create',
                        '-v',
                        mp['containerPath'],
                        '--name',
                        mp['sourceVolume'],
                        'alpine:3.4',
                        '/bin/true'
                    ]
                )

                # Copy any data into container. Patch for CircleCI security
                subprocess.check_call([
                        'docker',
                        'cp',
                        '--follow-link',
                        "%s/." % vol['host']['sourcePath'],
                        '%s:%s' % (vol['name'], mp['containerPath'])
                    ]
                )
                volumes.append(vol['name'])

            # Substitute Parameters
            command = job['containerProperties']['command']
            for param in parameters:
                command = map(lambda x: x.replace("Ref::%s" % param, parameters[param]), command)

            environments = job['containerProperties']['environment']
            for ovr in overrides:
                environments = filter(lambda x: x['name'] != ovr['name'], environments)
                environments.append(ovr)

            # Run Docker
            cmd = [
                    'docker',
                    'run',
                    '--network', # You must have a local network called "localnet" in bridge mode created.
                    'localnet',
                    '--name',
                    'batch_job'
                ]
            for vol in volumes:
                cmd.extend(["--volumes-from", vol])
            for env in environments:
                cmd.extend(["-e","%s=%s" % (env['name'],env['value'])])

            cmd.extend([job['containerProperties']['image']])
            cmd.extend(command)

            subprocess.check_call(cmd)

            # Copy data back into writable volumes
            for vol in job['containerProperties']['volumes']:
                mp = next(mp for mp in job['containerProperties']['mountPoints'] if mp['sourceVolume'] == vol['name'])
                if (mp['readOnly'] == False):
                    subprocess.check_call([
                            'docker',
                            'cp',
                            'batch_job:%s/.' % mp['containerPath'],
                            "%s" % vol['host']['sourcePath']
                        ]
                    )
        except:
            # Teardown Containers
            subprocess.call([
                    'docker',
                    'rm',
                    'batch_job'
                ] + volumes
            )
            raise BaseException("Failed to run batch job")
        else:
            # Teardown Containers
            subprocess.check_call([
                    'docker',
                    'rm',
                    'batch_job'
                ] + volumes
            )

        return {'jobName': kwargs['jobName'], 'jobId': 'local_batch_job'}
