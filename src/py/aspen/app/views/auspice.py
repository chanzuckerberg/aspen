import os
import json
import logging
import requests
logger = logging.getLogger(__name__)

from typing import Any, Iterable, Mapping, MutableSequence, Tuple
from urllib.parse import quote_plus, unquote_plus

import boto3
from flask import jsonify, session, redirect, url_for, make_response
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

@application.route("/api/auspice/<int:phylo_tree_id>", methods=["GET"])
@requires_auth
def auspice(phylo_tree_id: int):
    # with session_scope(application.DATABASE_INTERFACE) as db_session:
    #     profile = session["profile"]
        # user = (
        #     get_usergroup_query(db_session, profile["user_id"])
        #     .options(joinedload(User.group, Group.can_see))
        #     .one()
        # )

    view_string = url_for("auspice_view", _external=True, phylo_tree_id=phylo_tree_id)
    view_string = view_string.replace("https://", "")

    return redirect(f'https://nextstrain.org/fetch/{view_string}')

@application.route("/api/auspice/view/<int:phylo_tree_id>/auspice.json", methods=["GET"])
def auspice_view(phylo_tree_id: int):
    phylo_tree: PhyloTree
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        phylo_runs: Iterable[Tuple[PhyloRun, int]] = (
            db_session.query(PhyloRun)
            .options(joinedload(PhyloRun.outputs))
            .filter(
                or_(
                    PhyloRun.group_id == user.group_id,
                    user.system_admin,
                )
            )
            .filter(PhyloRun.workflow_status == WorkflowStatusType.COMPLETED)
        )

        for phylo_run in phylo_runs:
            for output in phylo_run.outputs:
                if isinstance(output, PhyloTree) and output.entity_id == phylo_tree_id:
                    phylo_tree = output
                    found = True
                    break

    s3_client = boto3.client("s3")

    s3_response = s3_client.get_object(Bucket=phylo_tree.s3_bucket, Key=phylo_tree.s3_key)
    f = s3_response.body
    response = make_response(f)
    response.headers['Content-Type'] = 'text/json'
    response.headers['Content-Disposition'] = 'attachment; filename=auspice.json'
    return response
