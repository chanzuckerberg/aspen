from typing import Optional

from boto3 import Session

from aspen.aws._region import region

_session: Optional[Session] = None


def session() -> Session:
    global _session

    if _session is None:
        _session = Session(region_name=region())

    return _session
