""" resource.py """
import os

class Resources(object):
    """ This class build a aws arn around specified resource types """

    @classmethod
    def get_arn(cls, service, resource, region='us-east-1', partition='aws'):
        """ get an arn from aws resource params """

        # IAM, Route53 dont require a region
        if service in ['iam', 'route53', 'artifact', 'cloudfront', 'organizations', 's3', 'waf']:
            region = ''

        return f"arn:{partition}:{service}:{region}:{cls.get_account()}:{resource}"

    @classmethod
    def get_account(cls):
        ''' return account id from env '''
        return os.getenv('AWS_ACCOUNT_ID', '*')
