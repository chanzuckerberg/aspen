import datetime
import json
import logging
import re
import warnings
from typing import (
    Any,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
)

import boto3
import pytz
import tqdm
from sqlalchemy import and_, or_
from sqlalchemy.orm import configure_mappers, joinedload, Session

from aspen.aws.s3 import S3UrlParser
from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import (
    Group,
    PhyloRun,
    PhyloTree,
    PublicRepositoryType,
    RegionType,
    Sample,
    UploadedPathogenGenome,
    WorkflowStatusType,
)
from aspen.phylo_tree.identifiers import get_names_from_tree
from covid_database import init_db as covidhub_init_db
from covid_database import SqlAlchemyInterface as CSqlAlchemyInterface
from covid_database import util as covidhub_database_util
from covid_database.models import covidtracker
from covid_database.models.enums import ConsensusGenomeStatus
from covid_database.models.ngs_sample_tracking import (
    ConsensusGenome,
    CZBID,
    DphCZBID,
    Project,
    SampleFastqs,
)

logger = logging.getLogger(__name__)


def covidhub_interface_from_secret(
    covidhub_aws_profile: str, secret_id: str
) -> CSqlAlchemyInterface:
    interface = covidhub_init_db(
        covidhub_database_util.get_db_uri(secret_id, aws_profile=covidhub_aws_profile)
    )
    return interface


def list_bucket(s3_resource, bucket: str, key_prefix: str) -> Iterator[str]:
    nexttoken = None
    while True:
        kwargs: Mapping[str, Any] = {}
        if nexttoken is not None:
            kwargs["ContinuationToken"] = nexttoken
        results = s3_resource.meta.client.list_objects_v2(
            Bucket=bucket, Prefix=key_prefix, **kwargs
        )
        for result in results["Contents"]:
            yield result["Key"]
        if not results["IsTruncated"]:
            return
        nexttoken = results["NextContinuationToken"]


def import_project(
    interface: SqlAlchemyInterface,
    covidhub_aws_profile: str,
    covidhub_secret_id: str,
    rr_project_id: str,
    aspen_group_id: int,
    s3_src_prefix: str,
    s3_dst_prefix: str,
):
    configure_mappers()
    covidhub_interface = covidhub_interface_from_secret(
        covidhub_aws_profile, covidhub_secret_id
    )
    covidhub_session: Session = covidhub_interface.make_session()

    with session_scope(interface) as session:
        project = (
            covidhub_session.query(Project)
            .options(
                joinedload(
                    Project.covidtracker_group, covidtracker.GroupToProjects.group
                )
            )
            .filter(Project.rr_project_id == rr_project_id)
            .one()
        )
        group: Group = session.query(Group).filter(Group.id == aspen_group_id).one()

        logger.info("Retrieving from COVIDHUB DB...")
        consensus_genomes: Collection[ConsensusGenome] = (
            covidhub_session.query(ConsensusGenome)
            .join(SampleFastqs, CZBID, Project)
            .distinct(CZBID.id)
            .filter(Project.rr_project_id == rr_project_id)
            .filter(
                or_(
                    ConsensusGenome.status == ConsensusGenomeStatus.PASSED_AUTO,
                    ConsensusGenome.status == ConsensusGenomeStatus.PASSED_MANUAL,
                )
            )
            .order_by(
                CZBID.id.desc(),
                ConsensusGenome.recovered_sites.desc(),
                ConsensusGenome.id.desc(),
            )
            .options(
                joinedload(ConsensusGenome.sample_fastqs)
                .joinedload(SampleFastqs.czb_id.of_type(DphCZBID))
                .joinedload(CZBID.genome_submission_info),
            )
            .all()
        )
        czbid_without_consensus_genomes: Iterable[DphCZBID] = (
            covidhub_session.query(DphCZBID)
            .join(Project)
            .filter(
                DphCZBID.czb_id.notin_(
                    {
                        consensus_genome.sample_fastqs.czb_id.czb_id
                        for consensus_genome in consensus_genomes
                    }
                )
            )
            .filter(Project.rr_project_id == rr_project_id)
            .options(
                joinedload(DphCZBID.sample_fastqs).joinedload(
                    SampleFastqs.consensus_genomes
                ),
                joinedload(DphCZBID.genome_submission_info),
            )
        )

        external_accessions = {
            consensus_genome.sample_fastqs.czb_id.external_accession
            for consensus_genome in tqdm.tqdm(consensus_genomes)
            if isinstance(consensus_genome.sample_fastqs.czb_id, DphCZBID)
        }
        external_accessions_to_samples: Mapping[str, Sample] = {
            sample.private_identifier: sample
            for sample in session.query(Sample).filter(
                and_(
                    Sample.submitting_group == group,
                    Sample.private_identifier.in_(external_accessions),
                )
            )
        }
        public_identifier_to_sample: MutableMapping[str, Sample] = dict()

        logger.info("Creating new objects...")
        for consensus_genome in tqdm.tqdm(consensus_genomes):
            czbid = consensus_genome.sample_fastqs.czb_id
            if not isinstance(czbid, DphCZBID):
                warnings.warn(
                    "consensus genome has non-dphczbid"
                    f"{consensus_genome.sample_fastqs.czb_id}"
                )
                continue

            sample = format_sample_for_dphczbid(
                project, group, czbid, consensus_genome, external_accessions_to_samples
            )
            public_identifier_to_sample[sample.public_identifier] = sample

        for czbid in tqdm.tqdm(czbid_without_consensus_genomes):
            sample = format_sample_for_dphczbid(
                project, group, czbid, None, external_accessions_to_samples
            )
            public_identifier_to_sample[sample.public_identifier] = sample

        pacific_time = pytz.timezone("US/Pacific")
        s3_src = boto3.session.Session(profile_name=covidhub_aws_profile).resource("s3")
        s3_dst = boto3.session.Session().resource("s3")

        src_prefix_url = S3UrlParser(s3_src_prefix)
        dst_prefix_url = S3UrlParser(s3_dst_prefix)
        for key in list_bucket(s3_src, src_prefix_url.bucket, src_prefix_url.key):
            key_prefix_removed = key[len(src_prefix_url.key) :]
            key_mo = re.match(
                r".*_(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})\.json",
                key,
            )
            if key_mo is None:
                logger.warning(
                    f"S3 object s3://{src_prefix_url.bucket}/{key} does not conform to"
                    " expected filename structure."
                )
                continue
            year, month, day = (
                2000 + int(key_mo["year"]),
                int(key_mo["month"]),
                int(key_mo["day"]),
            )
            dt = pacific_time.localize(
                datetime.datetime(year=year, month=month, day=day, hour=12)
            )

            data = s3_src.Bucket(src_prefix_url.bucket).Object(key).get()["Body"].read()

            json_decoded = json.loads(data.decode())
            tree = [json_decoded["tree"]]

            all_public_identifiers = get_names_from_tree(tree)

            all_uploaded_pathogen_genomes: Sequence[UploadedPathogenGenome] = [
                sample.uploaded_pathogen_genome
                for public_identifier, sample in public_identifier_to_sample.items()
                if sample.uploaded_pathogen_genome is not None
                and public_identifier in all_public_identifiers
            ]

            phylo_tree = PhyloTree(
                s3_bucket=dst_prefix_url.bucket,
                s3_key=dst_prefix_url.key + key_prefix_removed,
            )
            phylo_tree.constituent_samples = [
                uploaded_pathogen_genome.sample
                for uploaded_pathogen_genome in all_uploaded_pathogen_genomes
            ]

            workflow = PhyloRun(
                group=group,
                start_datetime=dt,
                end_datetime=dt,
                workflow_status=WorkflowStatusType.COMPLETED,
                software_versions={},
            )
            workflow.inputs = list(all_uploaded_pathogen_genomes)
            workflow.outputs = [phylo_tree]

            s3_dst.Bucket(phylo_tree.s3_bucket).Object(phylo_tree.s3_key).put(Body=data)

            print(
                f"s3://{src_prefix_url.bucket}/{key} ==>"
                f" s3://{phylo_tree.s3_bucket}/{phylo_tree.s3_key}"
            )


def format_sample_for_dphczbid(
    project: Project,
    group: Group,
    dphczbid: DphCZBID,
    consensus_genome: Optional[ConsensusGenome],
    external_accessions_to_samples: Mapping[str, Sample],
) -> Sample:
    if dphczbid.external_accession in (
        "OCPHL2207",
        "OCPHL2208",
    ):
        external_accession = f"{dphczbid.external_accession} ({dphczbid.czb_id})"
    else:
        external_accession = dphczbid.external_accession
    sample = external_accessions_to_samples.get(external_accession, None)
    if sample is None:
        sample = Sample(submitting_group=group, private_identifier=external_accession)

    sample.original_submission = {}
    sample.public_identifier = (
        f"USA/{dphczbid.submission_base}/{dphczbid.collection_date.year}"
    )
    sample.sample_collected_by = project.originating_lab
    sample.sample_collector_contact_address = project.originating_address
    sample.collection_date = dphczbid.collection_date
    sample.location = project.location
    sample.division = "California"
    sample.country = "USA"
    sample.region = RegionType.NORTH_AMERICA
    sample.organism = "SARS-CoV-2"

    if consensus_genome is not None:
        if sample.uploaded_pathogen_genome is None:
            sample.uploaded_pathogen_genome = UploadedPathogenGenome(
                sample=sample,
            )
        sample.uploaded_pathogen_genome.upload_date = dphczbid.date_received
        sample.uploaded_pathogen_genome.num_unambiguous_sites = (
            consensus_genome.recovered_sites
        )
        sample.uploaded_pathogen_genome.num_mixed = consensus_genome.ambiguous_sites
        sample.uploaded_pathogen_genome.num_missing_alleles = (
            consensus_genome.missing_sites
        )
        sample.uploaded_pathogen_genome.sequencing_depth = consensus_genome.avg_depth
        sample.uploaded_pathogen_genome.sequence = consensus_genome.fasta

        if dphczbid.genome_submission_info is not None:
            repository_type: Optional[PublicRepositoryType] = None
            if dphczbid.genome_submission_info.gisaid_accession is not None:
                repository_type = PublicRepositoryType.GISAID
                public_identifier = dphczbid.genome_submission_info.gisaid_accession
            elif dphczbid.genome_submission_info.genbank_accession is not None:
                repository_type = PublicRepositoryType.GENBANK
                public_identifier = dphczbid.genome_submission_info.genbank_accession

            if repository_type is not None:
                sample.uploaded_pathogen_genome.add_accession(
                    repository_type=repository_type,
                    public_identifier=public_identifier,
                )
    else:
        sample.czb_failed_genome_recovery = True

    return sample
