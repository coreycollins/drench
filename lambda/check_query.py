"""athena query check lambda for drench sdk"""
import boto3

def handler(event, context): #pylint:disable=unused-argument
    """pass parameter into athena query check"""
    client = boto3.client('athena', region_name='us-east-1')

    if 'query' in event:
        query = event['query']
    else:
        raise BaseException("No query message sent")

    response = client.start_query_execution(
        QueryExecutionId=query['QueryExecutionId']
    )

    return response['QueryExecution']['Status']['State']
