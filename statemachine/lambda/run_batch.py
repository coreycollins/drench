from __future__ import print_function
import json
import boto3
import os
import logging
import subprocess
import jsonpath_ng

logger = logging.getLogger()

"""
Event Format: {"jobQueue":"dev-queue", "jobDefinition":"sap-job-execution", "jobId":"batch_1234", "containerOverrides":[], "parameters":{}}
"""

def getenv():
    return os.getenv("LAMBDA_ENV") or "development"

def handler(event, context):
    client = boto3.client('batch', region_name='us-east-1')

    # Batch job parameters must be sent as {'batch':{}}
    if('batch' in event):
        batch = event['batch']
    else:
        raise BaseException("No batch job sent")

    result = client.describe_job_definitions(jobDefinitionName=batch['jobDefinition'], status='ACTIVE')
    job = result["jobDefinitions"][0]

    # Substitute parameters
    parameters = {}
    if ('parameters' in batch):
        for k,v in batch['parameters'].iteritems():
            try:
                expr = jsonpath_ng.parse(v)
                parameters[k] = expr.find(event)[0].value
            except:
                parameters[k] = v


    overrides = []
    if ('containerOverrides' in batch):
        overrides = batch['containerOverrides']

    if (getenv() != 'development'):
        # TODO: Run on batch
        print('Running')
    else:
        volumes = []

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
