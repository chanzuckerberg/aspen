import json
import os
import uuid
from typing import Any, Iterable, Mapping, MutableSequence, Set, Tuple

import boto3
from flask import jsonify, make_response, session
from sqlalchemy import func, or_
from sqlalchemy.orm import aliased, joinedload, Session

from aspen.app.app import application, requires_auth
from aspen.app.views.api_utils import format_datetime, get_usergroup_query
from aspen.database.connection import session_scope
from aspen.database.models import (
    DataType,
    PhyloRun,
    PhyloTree,
    PhyloTreeSamples,
    Sample,
    WorkflowStatusType,
)
from aspen.database.models.usergroup import Group, User
from aspen.error.recoverable import RecoverableError
from aspen.phylo_tree.identifiers import rename_nodes_on_tree

PHYLO_TREE_KEY = "phylo_trees"


@application.route("/api/phylo_trees", methods=["GET"])
@requires_auth
def phylo_trees():
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        profile = session["profile"]
        user = (
            get_usergroup_query(db_session, profile["user_id"])
            .options(joinedload(User.group).joinedload(Group.can_see))
            .one()
        )
        # TODO: Add subquery to fetch trees for which we have can-see permissions.
        phylo_run_alias = aliased(PhyloRun)
        phylo_runs: Iterable[Tuple[PhyloRun, int]] = (
            db_session.query(
                phylo_run_alias,
                (
                    db_session.query(func.count(1))
                    .select_from(Sample)
                    .join(PhyloTreeSamples)
                    .join(
                        PhyloTree,
                        PhyloTreeSamples.columns.phylo_tree_id == PhyloTree.entity_id,
                    )
                    .filter(
                        PhyloTree.producing_workflow_id == phylo_run_alias.workflow_id
                    )
                ).label("phylo_run_genome_count"),
            )
            .options(joinedload(phylo_run_alias.outputs))
            .filter(
                or_(
                    phylo_run_alias.group_id.in_(
                        db_session.query(Group.id)
                        .join(User)
                        .filter(User.auth0_user_id == profile["user_id"])
                        .subquery()
                    ),
                    user.system_admin,
                )
            )
            .filter(phylo_run_alias.workflow_status == WorkflowStatusType.COMPLETED)
        )

        # filter for only information we need in sample table view
        results: MutableSequence[Mapping[str, Any]] = list()
        for phylo_run, genome_count in phylo_runs:
            phylo_tree: PhyloTree
            for output in phylo_run.outputs:
                if isinstance(output, PhyloTree):
                    phylo_tree = output
                    break
            else:
                raise RecoverableError(
                    f"phylo run (workflow id={phylo_run.workflow_id}) does not have a"
                    " phylo tree output."
                )
            results.append(
                {
                    "phylo_tree_id": phylo_tree.entity_id,
                    "pathogen_genome_count": genome_count,
                    "completed_date": format_datetime(phylo_run.end_datetime),
                }
            )

        return jsonify({PHYLO_TREE_KEY: results})


def _process_phylo_tree(
    db_session: Session, phylo_tree_id: int, user_auth0_id: str
) -> dict:
    """Retrieves a phylo tree and renames the nodes on the tree for a given user."""
    user: User = (
        get_usergroup_query(db_session, user_auth0_id)
        .options(joinedload(User.group, Group.can_see))
        .one()
    )

    phylo_tree: PhyloTree = (
        db_session.query(PhyloTree)
        .filter(PhyloTree.entity_id == phylo_tree_id)
        .options(joinedload(PhyloTree.constituent_samples))
        .one()
    )

    can_see_group_ids: Set[int] = {user.group_id}
    can_see_group_ids.update(
        {
            can_see.owner_group_id
            for can_see in user.group.can_see
            if can_see.data_type == DataType.PRIVATE_IDENTIFIERS
        }
    )

    identifier_map: Mapping[str, str] = {
        sample.public_identifier: sample.private_identifier
        for sample in phylo_tree.constituent_samples
        if sample.submitting_group_id in can_see_group_ids
    }

    # TODO: add access control for this tree.
    # TODO: add a per-process shared AWS handle.
    s3 = boto3.resource("s3")

    data = (
        s3.Bucket(phylo_tree.s3_bucket).Object(phylo_tree.s3_key).get()["Body"].read()
    )
    json_data = json.loads(data)

    rename_nodes_on_tree([json_data["tree"]], identifier_map, "GISAID_ID")

    return json_data


@application.route("/api/phylo_tree/<int:phylo_tree_id>", methods=["GET"])
@requires_auth
def phylo_tree(phylo_tree_id: int):
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        phylo_tree_data = _process_phylo_tree(
            db_session, phylo_tree_id, session["profile"]["user_id"]
        )

    response = make_response(phylo_tree_data)
    response.headers["Content-Type"] = "application/json"
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={phylo_tree_id}.json"

    return response


@application.route("/api/auspice/view/<int:phylo_tree_id>", methods=["GET"])
@requires_auth
def auspice_view(phylo_tree_id: int):
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        phylo_tree_data = _process_phylo_tree(
            db_session, phylo_tree_id, session["profile"]["user_id"]
        )

        s3_resource = boto3.resource(
            "s3",
            endpoint_url=os.getenv("BOTO_ENDPOINT_URL") or None,
            config=boto3.session.Config(signature_version="s3v4"),
        )
        s3_bucket = application.aspen_config.EXTERNAL_AUSPICE_BUCKET
        s3_key = str(uuid.uuid4())
        s3_resource.Bucket(s3_bucket).Object(s3_key).put(
            Body=json.dumps(phylo_tree_data)
        )
        s3_client = s3_resource.meta.client

        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": s3_bucket, "Key": s3_key},
            ExpiresIn=3600,
        )

        return jsonify({"url": presigned_url})
