"""This module describes the entities and workflow for processing the gisaid dump."""
from __future__ import annotations

from typing import MutableSequence, Sequence

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.workflow import Workflow, WorkflowType


class RawGisaidDump(Entity):
    __tablename__ = "raw_gisaid_dump"
    __table_args__ = (UniqueConstraint("s3_bucket", "s3_key"),)

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)
    download_date = Column(DateTime, nullable=False)
    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": EntityType.RAW_GISAID_DUMP}

    @property
    def processed_gisaid_dumps(self) -> Sequence[ProcessedGisaidDump]:
        """A sequence of processed gisaid dumps generated from this raw gisaid dump."""
        results: MutableSequence[ProcessedGisaidDump] = list()
        for workflow, entities in self.get_children(ProcessedGisaidDump):
            results.extend(entities)

        return results


class ProcessedGisaidDump(Entity):
    __tablename__ = "processed_gisaid_dump"
    __table_args__ = (
        UniqueConstraint(
            "s3_bucket",
            "sequences_s3_key",
            name="uq_processed_gisaid_dump_s3_bucket_sequences",
        ),
        UniqueConstraint(
            "s3_bucket",
            "metadata_s3_key",
            name="uq_processed_gisaid_dump_s3_bucket_key",
        ),
    )

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)
    s3_bucket = Column(String, nullable=False)
    sequences_s3_key = Column(String, nullable=False)
    metadata_s3_key = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": EntityType.PROCESSED_GISAID_DUMP}

    @property
    def raw_gisaid_dump(self) -> RawGisaidDump:
        """The raw gisaid dump this processed gisaid dump was generated from."""
        parents = self.get_parents(RawGisaidDump)
        assert len(parents) == 1
        return parents[0]


class GisaidDumpWorkflow(Workflow):
    __tablename__ = "gisaid_workflows"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.PROCESS_GISAID_DUMP}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)


class AlignedGisaidDump(Entity):
    __tablename__ = "aligned_gisaid_dump"
    __table_args__ = (
        UniqueConstraint(
            "s3_bucket",
            "sequences_s3_key",
            name="uq_aligned_gisaid_dump_s3_bucket_sequences",
        ),
        UniqueConstraint(
            "s3_bucket",
            "metadata_s3_key",
            name="uq_aligned_gisaid_dump_s3_bucket_key",
        ),
    )

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)
    s3_bucket = Column(String, nullable=False)
    sequences_s3_key = Column(String, nullable=False)
    metadata_s3_key = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": EntityType.ALIGNED_GISAID_DUMP}


class GisaidAlignmentWorkflow(Workflow):
    __tablename__ = "gisaid_alignment_workflows"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.ALIGN_GISAID_DUMP}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
