import datetime
import json
import logging
import re
from typing import Any, Iterator, Mapping, MutableMapping, Sequence, Tuple

import boto3
import pytz
from sqlalchemy.orm import configure_mappers

from aspen.aws.s3 import S3UrlParser
from aspen.database.connection import session_scope, SqlAlchemyInterface
from aspen.database.models import (
    Group,
    PhyloRun,
    PhyloTree,
    Sample,
    UploadedPathogenGenome,
    WorkflowStatusType,
)
from aspen.phylo_tree.identifiers import get_names_from_tree

logger = logging.getLogger(__name__)


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


def import_trees(
    interface: SqlAlchemyInterface,
    covidhub_aws_profile: str,
    aspen_group_id: int,
    s3_src_prefix: str,
    s3_dst_prefix: str,
):
    configure_mappers()

    with session_scope(interface) as session:
        group: Group = session.query(Group).filter(Group.id == aspen_group_id).one()

        # load all samples that we know about.
        public_identifier_to_sample: MutableMapping[str, Sample] = {
            sample.public_identifier: sample for sample in session.query(Sample)
        }
        all_phylo_trees: Mapping[Tuple[str, str], PhyloTree] = {
            (phylo_run.s3_bucket, phylo_run.s3_key): phylo_run
            for phylo_run in (
                session.query(PhyloTree).join(PhyloRun).filter(PhyloRun.group == group)
            )
        }

        pacific_time = pytz.timezone("US/Pacific")
        s3_src = boto3.session.Session(profile_name=covidhub_aws_profile).resource("s3")
        s3_dst = boto3.session.Session().resource("s3")

        src_prefix_url = S3UrlParser(s3_src_prefix)
        dst_prefix_url = S3UrlParser(s3_dst_prefix)
        for key in list_bucket(s3_src, src_prefix_url.bucket, src_prefix_url.key):
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
            key_prefix_removed = key[len(src_prefix_url.key) :]

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

            phylo_tree = all_phylo_trees.get(
                (dst_prefix_url.bucket, dst_prefix_url.key + key_prefix_removed), None
            )
            if phylo_tree is None:
                phylo_tree = PhyloTree(
                    s3_bucket=dst_prefix_url.bucket,
                    s3_key=dst_prefix_url.key + key_prefix_removed,
                )
            phylo_tree.constituent_samples = [
                uploaded_pathogen_genome.sample
                for uploaded_pathogen_genome in all_uploaded_pathogen_genomes
            ]

            workflow = phylo_tree.producing_workflow
            if workflow is None:
                workflow = PhyloRun()
            workflow.group = group
            workflow.start_datetime = dt
            workflow.end_datetime = dt
            workflow.workflow_status = WorkflowStatusType.COMPLETED
            workflow.software_versions = {}
            workflow.inputs = list(all_uploaded_pathogen_genomes)
            workflow.outputs = [phylo_tree]

            s3_dst.Bucket(phylo_tree.s3_bucket).Object(phylo_tree.s3_key).put(Body=data)

            print(
                f"s3://{src_prefix_url.bucket}/{key} ==>"
                f" s3://{phylo_tree.s3_bucket}/{phylo_tree.s3_key}"
            )
