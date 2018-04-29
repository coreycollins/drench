""" Utils helper """

def get_arn(service, resource, region='us-east-1', partition='aws'):
    """ get an arn from aws resource params """
    account_id = '909533743566'

    # IAM, Route53 dont require a region
    if service in ['iam', 'route53', 'artifact', 'cloudfront', 'organizations', 's3', 'waf']:
        region = ''

    return "arn:{partition}:{service}:{region}:{account}:{resource}".format(
        partition=partition,
        service=service,
        region=region,
        account=account_id,
        resource=resource
    )
