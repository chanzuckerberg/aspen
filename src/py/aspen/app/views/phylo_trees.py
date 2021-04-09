import json
from typing import Any, Iterable, Mapping, MutableSequence, Tuple

import boto3
from flask import jsonify, session, make_response
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from aspen.app.app import application, requires_auth
from aspen.app.views.api_utils import format_datetime, get_usergroup_query
from aspen.database.connection import session_scope
from aspen.database.models import (
    PathogenGenome,
    PhyloRun,
    PhyloTree,
    Workflow,
    WorkflowInputs,
    WorkflowStatusType,
)
from aspen.database.models.usergroup import Group, User
from aspen.error.recoverable import RecoverableError

PHYLO_TREE_KEY = "phylo_trees"


@application.route("/api/phylo_trees", methods=["GET"])
@requires_auth
def phylo_trees():
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        profile = session["profile"]
        user = (
            get_usergroup_query(db_session, profile["user_id"])
            .options(joinedload(User.group, Group.can_see))
            .one()
        )
        # TODO: Add subquery to fetch trees for which we have can-see permissions.
        phylo_runs: Iterable[Tuple[PhyloRun, int]] = (
            db_session.query(
                PhyloRun,
                (
                    db_session.query(func.count(1))
                    .select_from(PathogenGenome)
                    .join(WorkflowInputs)
                    .join(Workflow)
                    .filter(Workflow.id == PhyloRun.workflow_id)
                ).label("phylo_run_genome_count"),
            )
            .options(joinedload(PhyloRun.outputs))
            .filter(
                or_(
                    PhyloRun.group_id.in_(
                        db_session.query(Group.id)
                        .join(User)
                        .filter(User.auth0_user_id == profile["user_id"])
                        .subquery()
                    ),
                    user.system_admin,
                )
            )
            .filter(PhyloRun.workflow_status == WorkflowStatusType.COMPLETED)
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


@application.route("/api/phylo_tree/<int:phylo_tree_id>", methods=["GET"])
@requires_auth
def phylo_tree(phylo_tree_id: int):
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        phylo_tree = (
            db_session.query(PhyloTree)
            .filter(PhyloTree.entity_id == phylo_tree_id)
            .one()
        )
        # TODO: add access control for this tree.
        # TODO: add a per-process shared AWS handle.
        s3 = boto3.resource("s3")

        data = (
            s3.Bucket(phylo_tree.s3_bucket)
            .Object(phylo_tree.s3_key)
            .get()["Body"]
            .read()
        )
        json_data = json.loads(data)

        # TODO: replace the public identifiers with the private identifiers we have
        # access to.
        response = make_response(json_data)
        response.headers['Content-Type'] = 'text/json'
        response.headers['Content-Disposition'] = f'attachment; filename={phylo_tree_id}.json'

        return response
