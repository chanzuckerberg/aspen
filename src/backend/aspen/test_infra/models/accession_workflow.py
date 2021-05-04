import datetime
from dataclasses import dataclass
from typing import Optional

from aspen.database.models import PublicRepositoryType


@dataclass
class AccessionWorkflowDirective:
    """This is a way to encapsulate the accession workflows hanging off of an entity."""

    start_datetime: datetime.datetime

    end_datetime: Optional[datetime.datetime]
    """Set to None if this workflow failed, otherwise this is the time the workflow
    succeeded.  If the workflow failed, the remaining fields in the dataclass are
    ignored."""

    repository_type: Optional[PublicRepositoryType]

    public_identifier: Optional[str]
