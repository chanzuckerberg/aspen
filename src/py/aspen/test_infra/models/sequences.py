from datetime import datetime

from aspen.database.models import (
    PublicRepositoryType,
    Sample,
    SequencingInstrumentType,
    SequencingProtocolType,
    SequencingReadsCollection,
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
