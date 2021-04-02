import datetime
import json
import logging
import re
import warnings
from dataclasses import dataclass
from typing import (
    Any,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
)

import boto3
import pytz
import tqdm
from auth0.v3 import authentication as auth0_authentication
from auth0.v3 import management as auth0_management
from sqlalchemy import and_, or_
from sqlalchemy.orm import configure_mappers, joinedload, Session

from aspen.aws.s3 import S3UrlParser
from aspen.config import config as aspen_config
from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import (
    Group,
    PhyloRun,
    PhyloTree,
    PublicRepositoryType,
    Sample,
    UploadedPathogenGenome,
    User,
    WorkflowStatusType,
)
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


@dataclass
class Auth0Entry:
    nickname: str
    email: str
    auth0_token: str


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


def get_names_from_tree(tree) -> Set[str]:
    results: Set[str] = set()
    for node in tree:
        results.add(node["name"])
        if "children" in node:
            results.update(get_names_from_tree(node["children"]))

    return results


def get_or_make_group(session: Session, name: str, address: str, email: str) -> Group:
    group = session.query(Group).filter(Group.name == name).one_or_none()
    if group is None:
        # copy the project info into the "group"
        group = Group(
            name=name,
            address=address,
            email=email,
        )
        session.add(group)

    return group


def import_project(
    interface: SqlAlchemyInterface,
    covidhub_aws_profile: str,
    covidhub_secret_id: str,
    rr_project_id: str,
    s3_src_prefix: str,
    s3_dst_prefix: str,
    auth0_usermap: Mapping[str, Auth0Entry],
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

        group, admin_group, cdph_group = (
            get_or_make_group(
                session,
                project.originating_lab,
                project.originating_address,
                # FIXME: this needs to be updated.
                email="fakeemail@dph.gov",
            ),
            get_or_make_group(
                session,
                "ADMIN",
                "123 Main St.",
                # FIXME: this needs to be updated.
                email="FAKE_EMAIL@gmail.com",
            ),
            get_or_make_group(
                session,
                "CDPH",
                "3701 N Freeway Blvd, Sacramento, CA 95834",
                # FIXME: this needs to be updated.
                email="cdph.internetadmin@cdph.ca.gov",
            ),
        )
        covidhub_group_to_aspen_group = {
            project.covidtracker_group.group: group,
            covidhub_session.query(covidtracker.Group)
            .filter(covidtracker.Group.name == "Admin")
            .one(): admin_group,
            covidhub_session.query(covidtracker.Group)
            .filter(covidtracker.Group.name == "CDPH")
            .one(): cdph_group,
        }

        covidhub_users: Iterable[covidtracker.UsersGroups] = covidhub_session.query(
            covidtracker.UsersGroups
        ).filter(
            or_(
                covidtracker.UsersGroups.group_id.in_(
                    covidhub_session.query(covidtracker.Group.id).filter(
                        covidtracker.Group.name.in_(["Admin", "CDPH"])
                    )
                ),
                covidtracker.UsersGroups.group_id.in_(
                    covidhub_session.query(covidtracker.GroupToProjects.group_id)
                    .join(Project)
                    .filter(Project.rr_project_id == rr_project_id)
                ),
            ),
        )

        # create the users!
        for covidhub_user in covidhub_users:
            # try to find the user in the auth0_usermap
            auth0_user = auth0_usermap.get(covidhub_user.user_id, None)
            if auth0_user is None:
                continue

            # try to create this user in the aspen db.
            user = (
                session.query(User).filter(User.email == auth0_user.email).one_or_none()
            )
            if user is None:
                user = User()

            user.name = auth0_user.nickname
            user.email = auth0_user.email
            user.auth0_user_id = auth0_user.auth0_token
            user.group_admin = False
            user.system_admin = covidhub_user.group.name == "Admin"
            user.group = covidhub_group_to_aspen_group[covidhub_user.group]

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
                .joinedload(SampleFastqs.czb_id)
                .joinedload(CZBID.genome_submission_info),
            )
            .all()
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
            if czbid.external_accession in (
                "OCPHL2207",
                "OCPHL2208",
            ):
                external_accession = f"{czbid.external_accession} ({czbid.czb_id}"
            else:
                external_accession = czbid.external_accession
            sample = external_accessions_to_samples.get(external_accession, None)
            if sample is None:
                sample = Sample(
                    submitting_group=group, private_identifier=external_accession
                )

            sample.original_submission = {}
            sample.public_identifier = (
                f"USA/{czbid.submission_base}/{czbid.collection_date.year}"
            )
            sample.sample_collected_by = project.originating_lab
            sample.sample_collector_contact_address = project.originating_address
            sample.collection_date = czbid.collection_date
            sample.location = project.location
            sample.division = "California"
            sample.country = "USA"
            sample.organism = "SARS-CoV-2"

            if sample.uploaded_pathogen_genome is None:
                sample.uploaded_pathogen_genome = UploadedPathogenGenome(
                    sample=sample,
                )
            sample.uploaded_pathogen_genome.upload_date = czbid.date_received
            sample.uploaded_pathogen_genome.num_unambiguous_sites = (
                consensus_genome.recovered_sites
            )
            sample.uploaded_pathogen_genome.num_mixed = consensus_genome.ambiguous_sites
            sample.uploaded_pathogen_genome.num_missing_alleles = (
                consensus_genome.missing_sites
            )
            sample.uploaded_pathogen_genome.sequencing_depth = (
                consensus_genome.avg_depth
            )
            sample.uploaded_pathogen_genome.sequence = consensus_genome.fasta

            if czbid.genome_submission_info is not None:
                repository_type: Optional[PublicRepositoryType] = None
                if czbid.genome_submission_info.gisaid_accession is not None:
                    repository_type = PublicRepositoryType.GISAID
                    public_identifier = czbid.genome_submission_info.gisaid_accession
                elif czbid.genome_submission_info.genbank_accession is not None:
                    repository_type = PublicRepositoryType.GENBANK
                    public_identifier = czbid.genome_submission_info.genbank_accession

                if repository_type is not None:
                    sample.uploaded_pathogen_genome.add_accession(
                        repository_type=repository_type,
                        public_identifier=public_identifier,
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


def retrieve_auth0_users(config: aspen_config.Config) -> Mapping[str, Auth0Entry]:
    """Retrieves an auth0 token and then retrieve a user list.  Each element of the list
    is a tuple of (name, email, auth0_token)."""
    domain = config.AUTH0_DOMAIN
    client_id = config.AUTH0_MANAGEMENT_CLIENT_ID
    client_secret = config.AUTH0_MANAGEMENT_CLIENT_SECRET

    get_token_response = auth0_authentication.GetToken(domain)
    token = get_token_response.client_credentials(
        client_id, client_secret, "https://{}/api/v2/".format(domain)
    )
    mgmt_api_token = token["access_token"]
    auth0_client = auth0_management.Auth0(domain, mgmt_api_token)

    all_users: MutableMapping[str, Auth0Entry] = dict()
    page = 0
    while True:
        try:
            users_response = auth0_client.users.list(page=page)
            if users_response["length"] == 0:
                # done!
                break

            # concatenate the results to all_users.
            for user in users_response["users"]:
                all_users[user["user_id"]] = Auth0Entry(
                    user["nickname"], user["email"], user["user_id"]
                )
        finally:
            page += 1

    return all_users
