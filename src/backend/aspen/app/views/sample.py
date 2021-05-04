from typing import Any, Mapping, MutableMapping, MutableSequence, Sequence, Set

from flask import jsonify, session
from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased, joinedload

from aspen.app.app import application, requires_auth
from aspen.app.views import api_utils
from aspen.app.views.api_utils import get_usergroup_query
from aspen.database.connection import session_scope
from aspen.database.models import Accession, DataType, Entity, Workflow, WorkflowType
from aspen.database.models.sample import Sample
from aspen.database.models.usergroup import Group, User

SAMPLE_KEY = "samples"


def _format_created_date(sample: Sample) -> str:
    if sample.sequencing_reads_collection is not None:
        return api_utils.format_datetime(sample.sequencing_reads_collection.upload_date)
    elif sample.uploaded_pathogen_genome is not None:
        return api_utils.format_datetime(sample.uploaded_pathogen_genome.upload_date)
    else:
        return "not yet uploaded"


def _format_gisaid_accession(
    sample: Sample, entity_id_to_accession_map: Mapping[int, Accession]
) -> str:
    uploaded_entity = sample.get_uploaded_entity()
    accession = entity_id_to_accession_map.get(uploaded_entity.entity_id, None)
    if accession is not None:
        return accession.public_identifier
    return "NOT SUBMITTED"


@application.route("/api/samples", methods=["GET"])
@requires_auth
def samples():
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        profile = session["profile"]

        user = (
            get_usergroup_query(db_session, profile["user_id"])
            .options(joinedload(User.group).joinedload(Group.can_see))
            .one()
        )

        cansee_groups_metadata: Set[int] = {
            cansee.owner_group_id
            for cansee in user.group.can_see
            if cansee.data_type == DataType.METADATA
        }
        cansee_groups_private_identifiers: Set[int] = {
            cansee.owner_group_id
            for cansee in user.group.can_see
            if cansee.data_type == DataType.PRIVATE_IDENTIFIERS
        }

        # load the samples.
        samples: Sequence[Sample] = (
            db_session.query(Sample)
            .options(
                joinedload(Sample.uploaded_pathogen_genome),
                joinedload(Sample.sequencing_reads_collection),
            )
            .filter(
                or_(
                    Sample.submitting_group_id == user.group_id,
                    Sample.submitting_group_id.in_(cansee_groups_metadata),
                    user.system_admin,
                )
            )
            .all()
        )
        sample_entity_ids: Sequence[int] = [
            sample.uploaded_pathogen_genome.entity_id
            if sample.uploaded_pathogen_genome is not None
            else sample.sequencing_reads_collection.entity_id
            for sample in samples
        ]

        # load the accessions.
        entity_alias = aliased(Entity)
        accessions: Sequence[Accession] = (
            db_session.query(Accession)
            .distinct(Accession.entity_id)
            .join(Accession.producing_workflow)
            .join(entity_alias, Workflow.inputs)
            .order_by(Accession.entity_id.desc())
            .filter(
                and_(
                    Workflow.workflow_type == WorkflowType.PUBLIC_REPOSITORY_SUBMISSION,
                    entity_alias.id.in_(sample_entity_ids),
                )
            )
            .options(
                joinedload(Accession.producing_workflow).joinedload(Workflow.inputs)
            )
            .all()
        )
        entity_id_to_accession_map: MutableMapping[int, Accession] = dict()
        for accession in accessions:
            for workflow_input in accession.producing_workflow.inputs:
                entity_id_to_accession_map[workflow_input.entity_id] = accession

        # filter for only information we need in sample table view
        results: MutableSequence[Mapping[str, Any]] = list()
        for sample in samples:
            returned_sample_data = {
                "public_identifier": sample.public_identifier,
                "upload_date": _format_created_date(sample),
                "collection_date": api_utils.format_date(sample.collection_date),
                "collection_location": sample.location,
                "gisaid": _format_gisaid_accession(sample, entity_id_to_accession_map),
            }

            if (
                sample.submitting_group_id == user.group_id
                or sample.submitting_group_id in cansee_groups_private_identifiers
                or user.system_admin
            ):
                returned_sample_data["private_identifier"] = sample.private_identifier

            results.append(returned_sample_data)

        return jsonify({SAMPLE_KEY: results})
