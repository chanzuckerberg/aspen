from sqlalchemy import Column, Float, ForeignKey, Integer, String, UniqueConstraint

from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.workflow import Workflow, WorkflowType


class Bam(Entity):
    __tablename__ = "bams"
    __table_args__ = (UniqueConstraint("s3_bucket", "s3_key"),)
    __mapper_args__ = {"polymorphic_identity": EntityType.BAM}

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)

    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)

    sequencing_depth = Column(Float, nullable=False)


class AlignRead(Workflow):
    __tablename__ = "align_read_workflows"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.ALIGN_READ}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
