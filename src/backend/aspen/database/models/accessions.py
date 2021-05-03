import datetime
import enum
from typing import Optional

import enumtables
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from aspen.database.models.base import base
from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.enum import Enum
from aspen.database.models.workflow import Workflow, WorkflowStatusType, WorkflowType


class PublicRepositoryType(enum.Enum):
    GISAID = "GISAID"
    NCBI_SRA = "NCBI_SRA"
    GENBANK = "GENBANK"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_PublicRepositoryTypeTable = enumtables.EnumTable(
    PublicRepositoryType,
    base,
    tablename="public_repository_types",
)


class Accession(Entity):
    """A single accession of an entity."""

    __tablename__ = "accessions"
    __table_args__ = (UniqueConstraint("repository_type", "public_identifier"),)
    __mapper_args__ = {"polymorphic_identity": EntityType.PUBLIC_REPOSITORY_SUBMISSION}

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)

    repository_type = Column(
        Enum(PublicRepositoryType),
        ForeignKey(_PublicRepositoryTypeTable.item_id),
        nullable=False,
    )

    public_identifier = Column(String, nullable=False)

    @staticmethod
    def attach_to_entity(
        entity: Entity,
        repository_type: PublicRepositoryType,
        public_identifier: str,
        workflow_start_datetime: Optional[datetime.datetime] = None,
        workflow_end_datetime: Optional[datetime.datetime] = None,
    ):
        assert not isinstance(entity, Accession)

        accession = Accession(
            repository_type=repository_type,
            public_identifier=public_identifier,
        )
        workflow = AccessionWorkflow(
            software_versions={},
            workflow_status=WorkflowStatusType.COMPLETED,
            start_datetime=workflow_start_datetime,
            end_datetime=workflow_end_datetime,
        )
        accession.producing_workflow = workflow
        entity.consuming_workflows.append(workflow)


class AccessionWorkflow(Workflow):
    __tablename__ = "accession_workflows"
    __mapper_args__ = {
        "polymorphic_identity": WorkflowType.PUBLIC_REPOSITORY_SUBMISSION
    }

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
