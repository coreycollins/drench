""" create aws placebo fixture for all tests """
import os
from unittest.mock import patch
import pytest
import boto3
import placebo

SESSION = boto3.Session()
PILL = placebo.attach(SESSION, data_path=os.path.join(os.curdir, "tests/mocks"))
PILL.playback()

def fake_boto3_client(*args, **kwargs):
    """ use mocked boto session """
    return SESSION.client(*args, **kwargs)

@pytest.fixture(scope="session", autouse=True)
def mock_aws():
    """ catch and replace boto3.client invocation """
    with patch('boto3.client', fake_boto3_client):
        yield
