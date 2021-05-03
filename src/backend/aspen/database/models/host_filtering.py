from __future__ import annotations

from typing import MutableSequence, Sequence, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.workflow import Workflow, WorkflowType

if TYPE_CHECKING:
    from aspen.database.models.sequences import (
        CalledPathogenGenome,
        SequencingReadsCollection,
    )


class HostFilteredSequencingReadsCollection(Entity):
    __tablename__ = "host_filtered_sequencing_reads_collections"
    __table_args__ = (UniqueConstraint("s3_bucket", "s3_key"),)
    __mapper_args__ = {"polymorphic_identity": EntityType.HOST_FILTERED_SEQUENCE_READS}

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)

    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)

    @property
    def sequencing_read(self) -> SequencingReadsCollection:
        """The sequencing read collection this host-filtered sequencing read collection
        was generated from."""
        # this import has to be here for circular dependencies reasons. :(
        from aspen.database.models.sequences import SequencingReadsCollection

        parents = self.get_parents(SequencingReadsCollection)
        assert len(parents) == 1
        return parents[0]

    @property
    def pathogen_genomes(self) -> Sequence[CalledPathogenGenome]:
        # this import has to be here for circular dependencies reasons. :(
        from aspen.database.models.sequences import CalledPathogenGenome

        results: MutableSequence[CalledPathogenGenome] = list()
        for workflow, entities in self.get_children(CalledPathogenGenome):
            results.extend(entities)

        return results


class FilterRead(Workflow):
    __tablename__ = "filter_read_workflows"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.FILTER_READ}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
