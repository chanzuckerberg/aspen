import collections
import datetime
import logging
import warnings
from typing import (
    Collection,
    DefaultDict,
    List,
    Mapping,
    MutableSequence,
    Optional,
    Tuple,
)

import tqdm
from sqlalchemy import or_
from sqlalchemy.orm import configure_mappers, joinedload, selectin_polymorphic, Session

from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import (
    Group,
    PublicRepositoryType,
    RegionType,
    Sample,
    UploadedPathogenGenome,
    Workflow,
)
from covid_database import init_db as covidhub_init_db
from covid_database import SqlAlchemyInterface as CSqlAlchemyInterface
from covid_database import util as covidhub_database_util
from covid_database.models import covidtracker
from covid_database.models.enums import ConsensusGenomeStatus
from covid_database.models.ngs_sample_tracking import (
    ConsensusGenome,
    CZBID,
    CZBIDRnaPlate,
    DphCZBID,
    InternalCZBID,
    Project,
    SampleFastqs,
)
from covid_database.models.qpcr_processing import (
    AccessionSample,
    Aliquoting,
    Extraction,
    QPCRPlate,
    QPCRResult,
    QPCRRun,
    RNAPlate,
    SamplePlate,
)

logger = logging.getLogger(__name__)


def covidhub_interface_from_secret(
    covidhub_aws_profile: str, secret_id: str
) -> CSqlAlchemyInterface:
    interface = covidhub_init_db(
        covidhub_database_util.get_db_uri(secret_id, aws_profile=covidhub_aws_profile)
    )
    return interface


def _get_external_accession(external_accession: str, czbid: CZBID) -> str:
    """Get the external accession.  If it is provided, use it as is.  Otherwise, create
    a string out of the czbid's submission base."""
    if external_accession is None:
        external_accession = f"UNKNOWN_{czbid.submission_base}"
        warnings.warn(
            f"CZBID {czbid} does not have an external accession.  Assigning as"
            f" {external_accession}"
        )
    return external_accession


def import_project(
    interface: SqlAlchemyInterface,
    covidhub_aws_profile: str,
    covidhub_secret_id: str,
    rr_project_id: str,
    aspen_group_id: int,
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
        group_czbids: Collection[CZBID] = (
            covidhub_session.query(CZBID)
            .join(Project)
            .filter(Project.rr_project_id == rr_project_id)
            .options(
                selectin_polymorphic(CZBID, [DphCZBID, InternalCZBID]),
                joinedload(CZBID.genome_submission_info),
            )
            .all()
        )

        # load a map of czbid name to czbid object.
        czbid_lookup_by_str: Mapping[str, CZBID] = {
            czbid.czb_id: czbid for czbid in group_czbids
        }

        czbid_to_consensus_genomes: Mapping[str, ConsensusGenome] = {
            consensus_genome.sample_fastqs.czb_id.czb_id: consensus_genome
            for consensus_genome in covidhub_session.query(ConsensusGenome)
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
                joinedload(ConsensusGenome.sample_fastqs).joinedload(
                    SampleFastqs.czb_id
                )
            )
            .all()
        }

        internal_czb_ids_metadata: Mapping[str, Tuple[str, datetime.datetime]] = {
            czbid: (
                _get_external_accession(external_accession, czbid_lookup_by_str[czbid]),
                collection_date,
            )
            for czbid, external_accession, collection_date in covidhub_session.query(
                InternalCZBID.czb_id.label("czb_id"),
                AccessionSample.location_submitter_id.label("external_accession"),
                QPCRRun.completed_at.label("collection_date"),
            )
            .join(
                Project,
                CZBIDRnaPlate,
                RNAPlate,
                Extraction,
                SamplePlate,
                AccessionSample,
                Aliquoting,
                QPCRPlate,
                QPCRRun,
            )
            .filter(Project.rr_project_id == rr_project_id)
            .filter(QPCRResult.well_id == CZBIDRnaPlate.well_id)
            .filter(AccessionSample.well_id == CZBIDRnaPlate.well_id)
            .group_by(
                Project.rr_project_id.label("project_id"),
                Project.collaborating_institution.label("project_name"),
                AccessionSample.location_submitter_id.label("external_accession"),
                InternalCZBID.czb_id.label("czb_id"),
                QPCRRun.completed_at.label("collection_date"),
            )
        }

        # verify that we have no duplicates for external accessions
        external_accession_to_czbids: DefaultDict[
            str, set[str]
        ] = collections.defaultdict(set)
        for czbid, (external_accession, _) in internal_czb_ids_metadata.items():
            external_accession_to_czbids[external_accession].add(czbid)
        czbids_to_process: MutableSequence[CZBID] = list()
        for external_accession, czbids in external_accession_to_czbids.items():
            if len(czbids) > 1:
                # gather up the information for each czbid representing the external
                # accesssion.
                # 1. number of recovered sites
                # 2. date
                czbids_sorted_by_value_desc: List[
                    Tuple[int, datetime.datetime, str]
                ] = list()
                for czbid in czbids:
                    consensus_genome = czbid_to_consensus_genomes.get(czbid, None)
                    czbids_sorted_by_value_desc.append(
                        (
                            consensus_genome.recovered_sites
                            if consensus_genome is not None
                            else -1,
                            internal_czb_ids_metadata[czbid][1],
                            czbid,
                        )
                    )
                    czbids_sorted_by_value_desc.sort(reverse=True)
                picked_czbid_str = czbids_sorted_by_value_desc[0][2]
                warnings.warn(
                    f"External accession {external_accession} represented by multiple"
                    f" czbids: {czbids}.  Choosing {picked_czbid_str} as the czbid for"
                    "this sample."
                )
                czbids_to_process.append(czbid_lookup_by_str[picked_czbid_str])
            else:
                czbids_to_process.append(czbid_lookup_by_str[czbids.pop()])

        # load the existing samples, store as a mapping between external accession to
        # sample.
        external_accessions_to_samples: Mapping[str, Sample] = {
            sample.private_identifier: sample
            for sample in (
                session.query(Sample)
                .filter(Sample.submitting_group == group)
                .options(
                    joinedload(Sample.uploaded_pathogen_genome)
                    .joinedload(UploadedPathogenGenome.consuming_workflows)
                    .joinedload(Workflow.outputs)
                )
            )
        }

        logger.info("Creating new objects...")
        for czbid in tqdm.tqdm(czbids_to_process):
            if isinstance(czbid, DphCZBID):
                external_accession = czbid.external_accession
                collection_date = czbid.collection_date
                date_received = czbid.date_received or czbid.collection_date
            elif isinstance(czbid, InternalCZBID):
                internal_metadata = internal_czb_ids_metadata[czbid.czb_id]
                external_accession = internal_metadata[0]
                collection_date = internal_metadata[1]
                date_received = internal_metadata[1]
            else:
                warnings.warn(f"czbid of unsupported type: {czbid}")
                continue

            sample = external_accessions_to_samples.get(external_accession, None)
            if sample is None:
                sample = Sample(
                    submitting_group=group, private_identifier=external_accession
                )

            sample.original_submission = {}
            sample.public_identifier = (
                f"USA/{czbid.submission_base}/{collection_date.year}"
            )
            sample.sample_collected_by = project.originating_lab
            sample.sample_collector_contact_address = project.originating_address
            sample.collection_date = collection_date
            sample.location = project.location
            sample.division = "California"
            sample.country = "USA"
            sample.region = RegionType.NORTH_AMERICA
            sample.organism = "SARS-CoV-2"

            consensus_genome = czbid_to_consensus_genomes.get(czbid.czb_id, None)
            if consensus_genome is not None:
                if sample.uploaded_pathogen_genome is None:
                    sample.uploaded_pathogen_genome = UploadedPathogenGenome(
                        sample=sample,
                    )
                sample.uploaded_pathogen_genome.upload_date = date_received
                sample.uploaded_pathogen_genome.num_unambiguous_sites = (
                    consensus_genome.recovered_sites
                )
                sample.uploaded_pathogen_genome.num_mixed = (
                    consensus_genome.ambiguous_sites
                )
                sample.uploaded_pathogen_genome.num_missing_alleles = (
                    consensus_genome.missing_sites
                )
                sample.uploaded_pathogen_genome.sequencing_depth = (
                    consensus_genome.avg_depth
                )
                sample.uploaded_pathogen_genome.sequence = consensus_genome.fasta

                # if it's a dphczbid, then it might have genome submission info.
                if (
                    isinstance(czbid, DphCZBID)
                    and czbid.genome_submission_info is not None
                ):
                    repository_type: Optional[PublicRepositoryType] = None
                    if czbid.genome_submission_info.gisaid_accession is not None:
                        repository_type = PublicRepositoryType.GISAID
                        public_identifier = (
                            czbid.genome_submission_info.gisaid_accession
                        )
                    elif czbid.genome_submission_info.genbank_accession is not None:
                        repository_type = PublicRepositoryType.GENBANK
                        public_identifier = (
                            czbid.genome_submission_info.genbank_accession
                        )

                    if repository_type is not None:
                        for accession in sample.uploaded_pathogen_genome.accessions():
                            if (
                                accession.repository_type == repository_type
                                and accession.public_identifier == public_identifier
                            ):
                                break
                        else:
                            sample.uploaded_pathogen_genome.add_accession(
                                repository_type=repository_type,
                                public_identifier=public_identifier,
                                workflow_start_datetime=datetime.datetime.now(),
                                workflow_end_datetime=datetime.datetime.now(),
                            )
            else:
                sample.czb_failed_genome_recovery = True
