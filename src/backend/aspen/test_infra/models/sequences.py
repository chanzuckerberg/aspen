import datetime
from typing import Tuple

from aspen.database.models import (
    AccessionWorkflow,
    PublicRepositoryType,
    Sample,
    SequencingInstrumentType,
    SequencingProtocolType,
    SequencingReadsCollection,
    UploadedPathogenGenome,
    WorkflowStatusType,
)
from aspen.test_infra.models.accession_workflow import AccessionWorkflowDirective


def sequencing_read_factory(
    sample: Sample,
    sequencing_instrument=SequencingInstrumentType.ILLUMINA_GENOME_ANALYZER_IIX,
    sequencing_protocol=SequencingProtocolType.ARTIC_V3,
    sequencing_date=None,
    s3_bucket="bucket",
    s3_key="key",
    accessions: Tuple[AccessionWorkflowDirective, ...] = (
        AccessionWorkflowDirective(
            datetime.datetime.now(),
            datetime.datetime.now(),
            PublicRepositoryType.GISAID,
            "gisaid_public_identifier",
        ),
    ),
) -> SequencingReadsCollection:
    sequencing_date = sequencing_date or datetime.datetime.now()
    sequencing_reads = SequencingReadsCollection(
        sample=sample,
        sequencing_instrument=sequencing_instrument,
        sequencing_protocol=sequencing_protocol,
        sequencing_date=sequencing_date,
        s3_bucket=s3_bucket,
        s3_key=s3_key,
    )
    for accession_workflow_directive in accessions:
        if accession_workflow_directive.end_datetime is None:
            sequencing_reads.consuming_workflows.append(
                AccessionWorkflow(
                    software_versions={},
                    workflow_status=WorkflowStatusType.FAILED,
                    start_datetime=accession_workflow_directive.start_datetime,
                )
            )
        else:
            assert accession_workflow_directive.repository_type is not None
            assert accession_workflow_directive.public_identifier is not None
            sequencing_reads.add_accession(
                repository_type=accession_workflow_directive.repository_type,
                public_identifier=accession_workflow_directive.public_identifier,
                workflow_start_datetime=accession_workflow_directive.start_datetime,
                workflow_end_datetime=accession_workflow_directive.end_datetime,
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
    upload_date=datetime.datetime.now(),
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
