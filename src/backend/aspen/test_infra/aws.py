import boto3
import pytest
from moto import mock_s3


@pytest.fixture(scope="session")
def mock_s3_resource():
    with mock_s3():
        s3_resource = boto3.resource("s3")
        yield s3_resource
