import logging
import os
from typing import Optional

import boto3
from flask import make_response, session
import requests

from aspen.app.app import application
from aspen.database.connection import session_scope
from aspen.database.models import PhyloTree
from aspen.error.recoverable import RecoverableError

logger = logging.getLogger(__name__)


@application.route(
    "/api/auspice/view/<int:phylo_tree_id>", methods=["GET"]
)
def auspice_view(phylo_tree_id: int):
    with session_scope(application.DATABASE_INTERFACE) as db_session:
        logger.info("SESSION: ", session)
        phylo_tree: Optional[PhyloTree] = (
            db_session.query(PhyloTree)
            .filter(PhyloTree.entity_id == phylo_tree_id)
            .one_or_none()
        )

        if not phylo_tree:
            raise RecoverableError(f"Phylo Tree {phylo_tree_id} not found.")

        s3_resource = boto3.resource(
            "s3",
            endpoint_url=os.getenv("BOTO_ENDPOINT_URL") or None,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        s3_client = s3_resource.meta.client

        presigned_url = (
            s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": phylo_tree.s3_bucket, "Key": phylo_tree.s3_key},
            ExpiresIn=3600
            )
        )

        return presigned_url

