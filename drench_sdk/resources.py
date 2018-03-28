""" resource.py """
import os

class Resources(object): # pylint: disable=too-few-public-methods
    """ This class build a aws arn around specified resource types """

    @classmethod
    def get_arn(cls, service, resource, region='us-east-1', partition='aws'):
        """ get an arn from aws resource params """
        account_id = os.getenv('AWS_ACCOUNT_ID', '*')
        env=os.getenv('DRENCH_ENV', '*')

        # IAM, Route53 dont require a region
        if service in ['iam', 'route53', 'artifact', 'cloudfront', 'organizations', 's3', 'waf']:
            region = ''

        subtype = ''
        if service == 'lambda':
            subtype = 'function'


        return f"arn:{partition}:{service}:{region}:{account_id}:{subtype}:{env}-{resource}"
