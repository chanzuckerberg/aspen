from typing import Dict, MutableSequence, Sequence

import requests

from aspen.aws._session import session


def _get_instance_id() -> str:
    document = requests.get(
        "http://169.254.169.254/latest/dynamic/instance-identity/document"
    ).json()
    return document["instanceId"]


def _get_tags() -> Sequence[Dict]:
    """Get all the EC2 tags attached to this instance."""
    results: MutableSequence[Dict] = list()
    nexttoken = None
    client = session().client(service_name="ec2")

    while True:
        kwargs: Dict = {}
        if nexttoken is not None:
            kwargs["NextToken"] = nexttoken
        response = client.describe_tags(**kwargs)
        results.extend(response["Tags"])
        nexttoken = response.get("NextToken", None)
        if nexttoken is None:
            break

    return results


def _get_environment_name() -> str:
    """Get all Elastic Beanstalk environment name."""
    instance_id = _get_instance_id()
    tags = _get_tags()

    for tag in tags:
        if (
            tag["Key"] == "elasticbeanstalk:environment-name"
            and tag["ResourceId"] == instance_id
            and tag["ResourceType"] == "instance"
        ):
            return tag["Value"]
    else:
        raise ValueError("Unable to find environment name")


def get_environment_suffix(prefix: str = "aspen-") -> str:
    """Get all Elastic Beanstalk environment name, excluding the aspen- prefix."""
    name = _get_environment_name()
    assert name.startswith(prefix)
    return name[len(prefix) :]
