'''update drench-api with stepp function step results'''
import requests


def handler(event, context): # pylint:disable=unused-argument
    '''lambda interface'''

    if 'payload' in event:
        payload = event['payload']
    else:
        raise BaseException("No result payload sent")

    headers = {'x-drench-token': 'test_token'}

    job_id = payload['step']['job_id']
    resp = requests.put(f'https://api.drench.io/jobs/{job_id}/steps',
                        data=payload,
                        headers=headers
                       )

    if resp.status_code == requests.codes['ok']:
        return 'SUCCEEDED'

    return 'FAILED'
