import enum
from typing import Mapping, MutableSequence, Union

import enumtables
from sqlalchemy import Column, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship

from aspen.database.models.base import base, idbase
from aspen.database.models.entity import _WORKFLOW_TABLENAME, Entity
from aspen.database.models.enum import Enum


class WorkflowType(enum.Enum):
    FILTER_READ = "FILTER_READ"
    ALIGN_READ = "ALIGN_READ"
    CALL_CONSENSUS = "CALL_CONSENSUS"
    PROCESS_GISAID_DUMP = "PROCESS_GISAID_DUMP"
    ALIGN_GISAID_DUMP = "ALIGN_GISAID_DUMP"
    PHYLO_RUN = "PHYLO_RUN"
    PUBLIC_REPOSITORY_SUBMISSION = "PUBLIC_REPOSITORY_SUBMISSION"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_WorkflowTypeTable = enumtables.EnumTable(
    WorkflowType,
    base,
    tablename="workflow_types",
)


class WorkflowStatusType(enum.Enum):
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_WorkflowStatusTypeTable = enumtables.EnumTable(
    WorkflowStatusType,
    base,
    tablename="workflow_status_types",
)


WorkflowInputs = Table(
    "workflow_inputs",
    base.metadata,
    Column("entity_id", ForeignKey(Entity.id), primary_key=True),
    Column("workflow_id", ForeignKey(f"{_WORKFLOW_TABLENAME}.id"), primary_key=True),
)


class Workflow(idbase):
    """A workflow describes some computational process undertaken on this system that
    takes one or more entities as inputs and produces one or more entities as
    outputs."""

    __tablename__ = _WORKFLOW_TABLENAME

    workflow_type = Column(
        Enum(WorkflowType),
        ForeignKey(_WorkflowTypeTable.item_id),
        nullable=False,
    )
    __mapper_args__: Mapping[str, Union[WorkflowType, Column]] = {
        "polymorphic_on": workflow_type
    }

    start_datetime = Column(
        DateTime, nullable=True, comment="datetime when the workflow is started."
    )
    end_datetime = Column(
        DateTime,
        nullable=True,
        comment="datetime when the workflow is ended.  this is only valid when the workflow's status is COMPLETED.",
    )

    workflow_status = Column(
        Enum(WorkflowStatusType),
        ForeignKey(_WorkflowStatusTypeTable.item_id),
        nullable=False,
    )

    software_versions = Column(
        JSON,
        nullable=False,
        comment=(
            "A mapping between all the tools used in this workflow and the version "
            "used."
        ),
    )

    inputs = relationship(
        Entity,
        secondary=WorkflowInputs,
        backref="consuming_workflows",
        uselist=True,
    )
    outputs: MutableSequence[Entity]


class SoftwareNames(str, enum.Enum):
    """Keys to be used in the software versions map (see Workflow.software_versions).
    Naming the versions consistently helps us ensure we're always using the same name to
    identify a particular piece of software."""

    ASPEN_WORKFLOW = "aspen_workflow"
    """This is the version of the aspen codebase from which the workflow is retrieved.
    Generally speaking, the workflow revision is going to be the same as the creation
    revision, but it can be different.  For instance, if the DB schema is updated
    between the time the workflow starts and when it finishes, we may update the tag.
    This way, the code reflects the state the database."""

    ASPEN_CREATION = "aspen_creation"
    """This is the version of the aspen codebase that is used to save the objects."""

    NCOV_INGEST = "ncov_ingest"
    """This is the version of the ncov-ingest repo
    (https://github.com/nextstrain/ncov-ingest/) for transforming the raw gisaid dumps
    into the sequence and metadata files."""

    NCOV = "ncov"
    """This is the version of the ncov repo (https://github.com/nextstrain/ncov/) for
    aligning gisaid dumps and for nextstrain runs."""

    ASPEN_DOCKER_IMAGE = "aspen_docker_image"
    """This is the version of the aspen docker image.  This includes the nextstrain
    tools used for gisaid alignment."""
