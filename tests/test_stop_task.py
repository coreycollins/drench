""" test job cencel from cloudwatch event """
from lambdas.stop_task import handler

def test_stop_batch():
    """ test batch cancel """
    event = {
        "detail":{
            "requestParameters": {
                "executionArn": "arn:aws:states:us-east-1:foo:execution:bar"
            }
        }
    }

    assert handler(event, None) == "OK"

def test_stop_glue():
    """ test glue cancel """
    event = {
        "detail":{
            "requestParameters": {
                "executionArn": "arn:aws:states:us-east-1:foo:execution:baz"
            }
        }
    }

    assert handler(event, None) == "OK"
