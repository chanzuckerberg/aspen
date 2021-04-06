from __future__ import annotations

import enum
from typing import MutableSequence, Sequence, TYPE_CHECKING

import enumtables
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    func,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, deferred, relationship

from aspen.database.models.base import base
from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.enum import Enum
from aspen.database.models.mixins import DictMixin
from aspen.database.models.sample import Sample
from aspen.database.models.workflow import Workflow, WorkflowType

if TYPE_CHECKING:
    from aspen.database.models.host_filtering import (
        HostFilteredSequencingReadsCollection,
    )


class SequencingInstrumentType(enum.Enum):
    ILLUMINA_HISEQ_X = "Illumina HiSeq X"
    ILLUMINA_HISEQ_X_FIVE = "Illumina HiSeq X Five"
    ILLUMINA_HISEQ_X_TEN = "Illumina HiSeq X Ten"
    ILLUMINA_GENOME_ANALYZER = "Illumina Genome Analyzer"
    ILLUMINA_GENOME_ANALYZER_II = "Illumina Genome Analyzer II"
    ILLUMINA_GENOME_ANALYZER_IIX = "Illumina Genome Analyzer IIx"
    ILLUMINA_HISCANSQ = "Illumina HiScanSQ"
    ILLUMINA_HISEQ_1000 = "Illumina HiSeq 1000"
    ILLUMINA_HISEQ_1500 = "Illumina HiSeq 1500"
    ILLUMINA_HISEQ_2000 = "Illumina HiSeq 2000"
    ILLUMINA_HISEQ_2500 = "Illumina HiSeq 2500"
    ILLUMINA_HISEQ_3000 = "Illumina HiSeq 3000"
    ILLUMINA_HISEQ_4000 = "Illumina HiSeq 4000"
    ILLUMINA_ISEQ_100 = "Illumina iSeq 100"
    ILLUMINA_NOVASEQ_6000 = "Illumina NovaSeq 6000"
    ILLUMINA_MINISEQ = "Illumina MiniSeq"
    ILLUMINA_MISEQ = "Illumina MiSeq"
    ILLUMINA_NEXTSEQ_500 = "Illumina NextSeq 500"
    ILLUMINA_NEXTSEQ_550 = "Illumina NextSeq 550"
    PACBIO_RS = "PacBio RS"
    PACBIO_RS_II = "PacBio RS II"
    PACBIO_SEQUEL = "PacBio Sequel"
    PACBIO_SEQUEL_II = "PacBio Sequel II"
    ION_TORRENT_PGM = "Ion Torrent PGM"
    ION_TORRENT_PROTON = "Ion Torrent Proton"
    ION_TORRENT_S5_XL = "Ion Torrent S5 XL"
    ION_TORRENT_S5 = "Ion Torrent S5"
    OXFORD_NANOPORE_GRIDION = "Oxford Nanopore GridION"
    OXFORD_NANOPORE_MINION = "Oxford Nanopore MinION"
    OXFORD_NANOPORE_PROMETHION = "Oxford Nanopore PromethION"
    BGISEQ_500 = "BGISEQ-500"
    DNBSEQ_T7 = "DNBSEQ-T7"
    DNBSEQ_G400 = "DNBSEQ-G400"
    DNBSEQ_G400_FAST = "DNBSEQ-G400 FAST"
    DNBSEQ_G50 = "DNBSEQ-G50"
    NOT_APPLICABLE = "Not Applicable"
    NOT_COLLECTED = "Not Collected"
    NOT_PROVIDED = "Not Provided"
    MISSING = "Missing"
    RESTRICTED_ACCESS = "Restricted Access"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_SequencingInstrumentTypeTable = enumtables.EnumTable(
    SequencingInstrumentType,
    base,
    tablename="sequencing_instrument_types",
)


class SequencingProtocolType(enum.Enum):
    ARTIC_V3 = "artic_v3"


# Create the enumeration table
# Pass your enum class and the SQLAlchemy declarative base to enumtables.EnumTable
_SequencingProtocolTypeTable = enumtables.EnumTable(
    SequencingProtocolType,
    base,
    tablename="sequencing_protocol_types",
)


class SequencingReadsCollection(Entity, DictMixin):
    __tablename__ = "sequencing_reads_collections"
    __table_args__ = (UniqueConstraint("s3_bucket", "s3_key"),)
    __mapper_args__ = {"polymorphic_identity": EntityType.SEQUENCING_READS}

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)
    sample_id = Column(Integer, ForeignKey(Sample.id), unique=True, nullable=False)
    sample = relationship(
        Sample,
        backref=backref("sequencing_reads_collection", uselist=False),
    )

    sequencing_instrument = Column(
        Enum(SequencingInstrumentType),
        ForeignKey(_SequencingInstrumentTypeTable.item_id),
        nullable=False,
    )
    sequencing_protocol = Column(
        Enum(SequencingProtocolType),
        ForeignKey(_SequencingProtocolTypeTable.item_id),
        nullable=False,
    )

    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)

    sequencing_date = Column(Date)
    upload_date = Column(DateTime, nullable=False, server_default=func.now())

    @property
    def host_filtered_sequencing_reads(
        self,
    ) -> Sequence[HostFilteredSequencingReadsCollection]:
        # this import has to be here for circular dependencies reasons. :(
        from aspen.database.models.host_filtering import (
            HostFilteredSequencingReadsCollection,
        )

        results: MutableSequence[HostFilteredSequencingReadsCollection] = list()
        for workflow, entities in self.get_children(
            HostFilteredSequencingReadsCollection
        ):
            results.extend(entities)

        return results

    @property
    def pathogen_genomes(self) -> Sequence[CalledPathogenGenome]:
        return [
            pathogen_genome
            for host_filtered_sequencing_reads_collection in self.host_filtered_sequencing_reads
            for pathogen_genome in host_filtered_sequencing_reads_collection.pathogen_genomes
        ]


class PathogenGenome(Entity):
    __tablename__ = "pathogen_genomes"

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)
    sequence = deferred(Column(String, nullable=False), raiseload=True)

    # statistics for the pathogen genome

    num_unambiguous_sites = Column(
        Integer, nullable=False, comment="Number of sites with allele A, C, T, or G"
    )

    num_missing_alleles = Column(
        Integer,
        nullable=False,
        comment=(
            "Number of sites with N, the missing allele,"
            " typically indicating low depth"
        ),
    )

    num_mixed = Column(
        Integer,
        nullable=False,
        comment=(
            "Number of sites with an ambiguous allele, e.g. M, K, Y, etc.,"
            " indicating support for 2 or more alleles in the reads."
        ),
    )


class UploadedPathogenGenome(PathogenGenome):
    __tablename__ = "uploaded_pathogen_genomes"
    __mapper_args__ = {"polymorphic_identity": EntityType.UPLOADED_PATHOGEN_GENOME}

    pathogen_genome_id = Column(
        Integer, ForeignKey(PathogenGenome.entity_id), primary_key=True
    )
    sample_id = Column(Integer, ForeignKey(Sample.id), unique=True, nullable=False)
    sample = relationship(
        Sample,
        backref=backref("uploaded_pathogen_genome", uselist=False),
    )

    sequencing_depth = Column(Float)
    upload_date = Column(DateTime, nullable=False, server_default=func.now())


class CalledPathogenGenome(PathogenGenome):
    __tablename__ = "called_pathogen_genomes"
    __mapper_args__ = {"polymorphic_identity": EntityType.CALLED_PATHOGEN_GENOME}

    pathogen_genome_id = Column(
        Integer, ForeignKey(PathogenGenome.entity_id), primary_key=True
    )


class CallConsensus(Workflow):
    __tablename__ = "call_consensus_workflows"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.CALL_CONSENSUS}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
