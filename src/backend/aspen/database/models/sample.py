from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING, Union

import enumtables
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    JSON,
    sql,
    String,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship

from aspen.database.models.base import base, idbase
from aspen.database.models.enum import Enum
from aspen.database.models.mixins import DictMixin
from aspen.database.models.usergroup import Group

if TYPE_CHECKING:
    from .sequences import SequencingReadsCollection, UploadedPathogenGenome


class RegionType(enum.Enum):
    AFRICA = "Africa"
    ASIA = "Asia"
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    OCEANIA = "Oceania"
    SOUTH_AMERICA = "South America"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_RegionTypeTable = enumtables.EnumTable(
    RegionType,
    base,
    tablename="region_types",
)


class Sample(idbase, DictMixin):  # type: ignore
    """A physical sample.  Multiple sequences can be taken of each physical sample."""

    __tablename__ = "samples"
    __table_args__ = (UniqueConstraint("submitting_group_id", "private_identifier"),)

    submitting_group_id = Column(
        Integer,
        ForeignKey(Group.id),
        nullable=False,
    )
    submitting_group = relationship(Group, backref=backref("samples", uselist=True))  # type: ignore
    private_identifier = Column(
        String,
        nullable=False,
        comment=(
            "This is the private identifier groups (DPHs) will use to map data back to "
            "their internal databases."
        ),
    )
    original_submission = Column(
        JSON,
        nullable=False,
        comment="This is the original metadata submitted by the user.",
    )

    public_identifier = Column(
        String,
        nullable=False,
        unique=True,
        comment="This is the public identifier we assign to this sample.",
    )

    sample_collected_by = Column(
        String,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "sample_collected_by",
            }
        },
    )

    sample_collector_contact_email = Column(
        String,
        nullable=True,
        info={
            "schema_mappings": {
                "PHA4GE": "sample_collector_contact_email",
            }
        },
    )

    sample_collector_contact_address = Column(
        String,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "sample_collector_contact_address",
            }
        },
    )

    authors = Column(
        JSONB,
        nullable=False,
        default=text("'[]'::jsonb"),
        server_default=text("'[]'::jsonb"),
    )

    collection_date = Column(
        Date,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "sample_collection_date",
            }
        },
    )

    # location
    location = Column(String, nullable=False)
    division = Column(
        String,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "geo_loc_name_state_province_region",
            }
        },
    )
    country = Column(
        String,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "geo_loc_name_country",
            }
        },
    )
    region = Column(
        Enum(RegionType),
        ForeignKey(_RegionTypeTable.item_id),
        nullable=False,
        comment="This is the continent this sample was collected from.",
    )

    organism = Column(
        String,
        nullable=False,
        info={
            "schema_mappings": {
                "PHA4GE": "organism",
            }
        },
    )

    host = Column(
        String,
        nullable=True,
        default="human",
        info={
            "schema_mappings": {
                "PHA4GE": "host_common_name",
            }
        },
    )

    purpose_of_sampling = Column(
        String,
        nullable=True,
        info={
            "schema_mappings": {
                "PHA4GE": "purpose_of_sampling",
            }
        },
    )

    specimen_processing = Column(
        String,
        nullable=True,
        info={
            "schema_mappings": {
                "PHA4GE": "specimen_processing",
            }
        },
    )

    czb_failed_genome_recovery = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=sql.expression.false(),
        comment=(
            "This is set to true iff this is sample sequenced by CZB and failed genome "
            "recovery."
        ),
    )

    sequencing_reads_collection: Optional[SequencingReadsCollection]
    uploaded_pathogen_genome: Optional[UploadedPathogenGenome]

    def get_uploaded_entity(
        self,
    ) -> Union[SequencingReadsCollection, UploadedPathogenGenome]:
        if self.sequencing_reads_collection is not None:
            return self.sequencing_reads_collection
        elif self.uploaded_pathogen_genome is not None:
            return self.uploaded_pathogen_genome
        raise ValueError(
            "Sample has neither sequencing reads nor uploaded pathogen genome."
        )
