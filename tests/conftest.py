import pytest
import os
from unittest.mock import patch
import boto3
import placebo

def fake_boto3_client(*args, **kwargs):
    session = boto3.Session()

    pill = placebo.attach(session, data_path=os.path.join(os.curdir, "tests/mocks"))
    pill.playback()

    return session.client(*args, **kwargs)

@pytest.fixture(scope="session", autouse=True)
def mock_aws():
    with patch('boto3.client', fake_boto3_client):
        yield
