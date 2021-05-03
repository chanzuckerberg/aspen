import os


def region():
    return os.environ.get("AWS_REGION")
