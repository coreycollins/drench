""" resource.py """
import os

class Resources(object): # pylint: disable=too-few-public-methods
    """ This class build a aws arn around specified resource types """

    @classmethod
    def get_arn(cls, service, resource_type, resource, region='us-east-1', partition='aws'):
        """ get an arn from aws resource params """
        account_id = os.getenv('AWS_ACCOUNT_ID', '*')

        # IAM, Route53 dont require a region
        if service in ['iam', 'route53', 'artifact', 'cloudfront', 'organizations', 's3', 'waf']:
            region = ''

        #TODO elif this: not all services have resourcetypes, and some specify
        #   resourcetype/resource
        #        rather than
        #   resourcetype:resource
        # see https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
        return f"arn:{partition}:{service}:{region}:{account_id}:{resource_type}:{resource}"
