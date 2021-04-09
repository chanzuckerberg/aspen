from __future__ import annotations

import datetime
import enum
from typing import (
    Mapping,
    MutableSequence,
    Optional,
    Sequence,
    Tuple,
    Type,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

import enumtables
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from aspen.database.models.base import base, idbase
from aspen.database.models.enum import Enum

if TYPE_CHECKING:
    from aspen.database.models.accessions import Accession, PublicRepositoryType
    from aspen.database.models.workflow import Workflow


_WORKFLOW_TABLENAME = "workflows"  # need this for a forward reference.


class EntityType(enum.Enum):
    SEQUENCING_READS = "SEQUENCING_READS"
    UPLOADED_PATHOGEN_GENOME = "UPLOADED_PATHOGEN_GENOME"
    CALLED_PATHOGEN_GENOME = "CALLED_PATHOGEN_GENOME"
    HOST_FILTERED_SEQUENCE_READS = "HOST_FILTERED_SEQUENCE_READS"
    BAM = "BAM"
    RAW_GISAID_DUMP = "RAW_GISAID_DUMP"
    PROCESSED_GISAID_DUMP = "PROCESSED_GISAID_DUMP"
    ALIGNED_GISAID_DUMP = "ALIGNED_GISAID_DUMP"
    PHYLO_TREE = "PHYLO_TREE"
    PUBLIC_REPOSITORY_SUBMISSION = "PUBLIC_REPOSITORY_SUBMISSION"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_EntityTypeTable = enumtables.EnumTable(
    EntityType,
    base,
    tablename="entity_types",
)


EntityGenericType = TypeVar("EntityGenericType", bound="Entity")


class Entity(idbase):  # type: ignore
    """A piece of data in the system.  It is represented as a file, though not always
    local to the system."""

    __tablename__ = "entities"
    entity_type = Column(
        Enum(EntityType),
        ForeignKey(_EntityTypeTable.item_id),
        nullable=False,
    )

    __mapper_args__: Mapping[str, Union[EntityType, Column]] = {
        "polymorphic_on": entity_type
    }

    consuming_workflows: MutableSequence[Workflow]

    producing_workflow_id = Column(Integer, ForeignKey(f"{_WORKFLOW_TABLENAME}.id"))
    producing_workflow = relationship(  # type: ignore
        "Workflow", backref=backref("outputs", uselist=True)
    )

    def get_parents(
        self,
        type_filter: Optional[Type[EntityGenericType]] = None,
    ) -> Sequence[EntityGenericType]:
        """Find the workflow that produced this entity, if any.  Then enumerate all the
        inputs to that workflow of a given type ``type_filter``.  If a type is not
        specified, then all the inputs to the workflow producing this entity are
        returned."""
        filt: Type[EntityGenericType] = (
            type_filter if type_filter is not None else Entity
        )

        if self.producing_workflow is None:
            return []

        return [
            workflow_input
            for workflow_input in self.producing_workflow.inputs
            if isinstance(workflow_input, filt)
        ]

    def get_children(
        self,
        type_filter: Optional[Type[EntityGenericType]] = None,
    ) -> Sequence[Tuple[Workflow, Sequence[EntityGenericType]]]:
        """Find all the workflows that consume this entity and produce outputs of a
        given type ``type_filter``.  If a type is not specified, then all the workflows
        that consume this entity and all their outputs are returned."""
        filt: Type[EntityGenericType] = (
            type_filter if type_filter is not None else Entity
        )
        results: MutableSequence[Tuple[Workflow, Sequence[EntityGenericType]]] = list()

        for workflow in self.consuming_workflows:
            tup = (
                workflow,
                [
                    workflow_output
                    for workflow_output in workflow.outputs
                    if isinstance(workflow_output, filt)
                ],
            )

            if len(tup[1]) > 0:
                results.append(tup)

        return results

    def accessions(self) -> Sequence[Accession]:
        from .accessions import Accession

        results: MutableSequence[Accession] = list()
        for workflow, accessions in self.get_children(Accession):
            results.extend(accessions)
        return results

    def add_accession(
        self,
        repository_type: PublicRepositoryType,
        public_identifier: str,
        workflow_start_datetime: Optional[datetime.datetime] = None,
        workflow_end_datetime: Optional[datetime.datetime] = None,
    ):
        """Adds an accession to this object."""
        from .accessions import Accession

        Accession.add_to_entity(
            self,
            repository_type,
            public_identifier,
            workflow_start_datetime,
            workflow_end_datetime,
        )
