from datetime import datetime

from aspen.database.models import (
    PublicRepositoryType,
    Sample,
    SequencingInstrumentType,
    SequencingProtocolType,
    SequencingReadsCollection,
    UploadedPathogenGenome,
)


def sequencing_read_factory(
    sample: Sample,
    sequencing_instrument=SequencingInstrumentType.ILLUMINA_GENOME_ANALYZER_IIX,
    sequencing_protocol=SequencingProtocolType.ARTIC_V3,
    sequencing_date=None,
    s3_bucket="bucket",
    s3_key="key",
    accessions={
        PublicRepositoryType.GISAID: "gisaid_public_identifier",
    },
) -> SequencingReadsCollection:
    sequencing_date = sequencing_date or datetime.now()
    sequencing_reads = SequencingReadsCollection(
        sample=sample,
        sequencing_instrument=sequencing_instrument,
        sequencing_protocol=sequencing_protocol,
        sequencing_date=sequencing_date,
        s3_bucket=s3_bucket,
        s3_key=s3_key,
    )
    for public_repository_type, public_identifier in accessions.items():
        sequencing_reads.add_accession(
            repository_type=public_repository_type,
            public_identifier=public_identifier,
        )
    return sequencing_reads


def uploaded_pathogen_genome_factory(
    sample,
    sequence=">test1\nNTCGGCG",
    num_unambiguous_sites=1,
    num_missing_alleles=0,
    num_mixed=0,
    pangolin_lineage=None,
    pangolin_probability=None,
    pangolin_version=None,
    pangolin_last_updated=None,
    sequencing_depth=0.1,
    upload_date=datetime.now(),
):
    return UploadedPathogenGenome(
        sample=sample,
        sequence=sequence,
        num_unambiguous_sites=num_unambiguous_sites,
        num_missing_alleles=num_missing_alleles,
        num_mixed=num_mixed,
        pangolin_lineage=pangolin_lineage,
        pangolin_probability=pangolin_probability,
        pangolin_version=pangolin_version,
        pangolin_last_updated=pangolin_last_updated,
        sequencing_depth=sequencing_depth,
        upload_date=upload_date,
    )
