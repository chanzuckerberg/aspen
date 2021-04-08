import datetime
import json
from operator import and_, or_
from pathlib import Path
from typing import Iterable, MutableSequence, Type

import boto3
import click
from IPython.terminal.embed import InteractiveShellEmbed
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import expression

from aspen import covidhub_import
from aspen.cli.toplevel import cli
from aspen.config.config import Config, RemoteDatabaseConfig
from aspen.config.development import DevelopmentConfig
from aspen.config.local import LocalConfig
from aspen.database.connection import (
    enable_profiling,
    get_db_uri,
    init_db,
    session_scope,
)
from aspen.database.models import *  # noqa: F401, F403
from aspen.database.models import (
    AlignedGisaidDump,
    Entity,
    Group,
    PathogenGenome,
    PhyloRun,
    Sample,
    SequencingReadsCollection,
    Workflow,
    WorkflowStatusType,
)
from aspen.database.schema import create_tables_and_schema


@cli.group()
@click.option("--local", "config_cls", flag_value=DevelopmentConfig, default=True)
@click.option("--remote", "config_cls", flag_value=RemoteDatabaseConfig)
@click.option("--docker", "config_cls", flag_value=LocalConfig)
@click.pass_context
def db(ctx, config_cls: Type[Config]):
    # TODO: support multiple runtime environments.
    config = config_cls()
    ctx.obj["CONFIG"] = config
    ctx.obj["ENGINE"] = init_db(get_db_uri(config))


@db.command("set-passwords-from-secret")
@click.pass_context
def set_passwords_from_secret(ctx):
    this_file = Path(__file__)
    root = this_file.parent.parent.parent.parent.parent
    default_db_credentials_file = root / "terraform.tfvars.json"
    with default_db_credentials_file.open("r") as fh:
        default_db_credentials = json.load(fh)["db_credentials"]
    admin_username = default_db_credentials["admin_username"]
    admin_password = default_db_credentials["admin_password"]

    secrets = RemoteDatabaseConfig().AWS_SECRET

    # find the db instance
    rds = boto3.client("rds")
    response = rds.describe_db_instances(DBInstanceIdentifier="aspen-db")
    instance_info = response["DBInstances"][0]
    instance_address = instance_info["Endpoint"]["Address"]
    instance_port = instance_info["Endpoint"]["Port"]
    db_interface = init_db(
        f"postgresql://{admin_username}:{admin_password}@{instance_address}:{instance_port}/aspen_db"
    )

    for username, password in (
        (admin_username, secrets["DB"]["admin_password"]),
        (default_db_credentials["rw_username"], secrets["DB"]["rw_password"]),
        (default_db_credentials["ro_username"], secrets["DB"]["ro_password"]),
    ):
        db_interface.engine.execute(f"""ALTER USER {username} PASSWORD '{password}'""")


@db.command("create")
@click.pass_context
def create_db(ctx):
    create_tables_and_schema(ctx.obj["ENGINE"])


@db.command("interact")
@click.option("--profile/--no-profile", default=False)
@click.pass_context
def interact(ctx, profile):
    # these are injected into the IPython scope, but they appear to be unused.
    engine = ctx.obj["ENGINE"]  # noqa: F841

    if profile:
        enable_profiling()

    shell = InteractiveShellEmbed()
    shell()


@db.command("import-covidhub-project")
@click.option("--covidhub-aws-profile", type=str, required=True)
@click.option("--covidhub-db-secret", default="cliahub/cliahub_test_db")
@click.option("--rr-project-id", type=str, required=True)
@click.option("--s3-src-prefix", type=str, required=True)
@click.option("--s3-dst-prefix", type=str, required=True)
@click.pass_context
def import_covidhub_project(
    ctx,
    covidhub_aws_profile,
    covidhub_db_secret,
    rr_project_id,
    s3_src_prefix,
    s3_dst_prefix,
):
    # these are injected into the IPython scope, but they appear to be unused.
    config, engine = ctx.obj["CONFIG"], ctx.obj["ENGINE"]

    auth0_usermap = covidhub_import.retrieve_auth0_users(config)

    covidhub_import.import_project(
        engine,
        covidhub_aws_profile,
        covidhub_db_secret,
        rr_project_id,
        s3_src_prefix,
        s3_dst_prefix,
        auth0_usermap,
    )


@db.command("create-phylo-run")
@click.option(
    "--group-name",
    type=str,
    required=True,
    help="Name of the group to create the phylo run under.",
)
@click.option("--all-group-sequences", is_flag=True, required=False, default=False)
@click.option("samples", "--sample", type=str, required=False, multiple=True)
@click.option("--aligned-gisaid-dump-id", type=int, required=False, default=None)
@click.option(
    "--builds-template-file",
    type=str,
    required=False,
    default="workflows/setup_nextstrain_run/builds_template.yaml",
)
@click.option("--builds-template-args", type=str, required=True)
@click.pass_context
def create_phylo_run(
    ctx,
    group_name,
    all_group_sequences,
    samples,
    aligned_gisaid_dump_id,
    builds_template_file,
    builds_template_args,
):
    # these are injected into the IPython scope, but they appear to be unused.
    engine = ctx.obj["ENGINE"]

    with session_scope(engine) as session:
        group = session.query(Group).filter(Group.name == group_name).one()

        all_samples: Iterable[Sample] = (
            session.query(Sample)
            .filter(
                or_(
                    Sample.public_identifier.in_(samples),
                    and_(
                        expression.true()
                        if all_group_sequences
                        else expression.false(),
                        Sample.submitting_group == group,
                    ),
                )
            )
            .options(
                joinedload(Sample.sequencing_reads_collection)
                .joinedload(SequencingReadsCollection.consuming_workflows)
                .joinedload(Workflow.outputs)
                .joinedload(Entity.consuming_workflows)
                .joinedload(Workflow.outputs)
                .joinedload(Entity.consuming_workflows)
                .joinedload(Workflow.outputs),
                joinedload(Sample.uploaded_pathogen_genome),
            )
        )

        pathogen_genomes: MutableSequence[PathogenGenome] = list()
        for sample in all_samples:
            if sample.sequencing_reads_collection is not None:
                sample_pathogen_genomes = (
                    sample.sequencing_reads_collection.pathogen_genomes
                )
                # TODO: We are blindly using the first pathogen genome we encounter.  It
                # should probably be based on some heuristic.
                if len(sample_pathogen_genomes) > 0:
                    pathogen_genomes.append(sample_pathogen_genomes[0])
            elif sample.uploaded_pathogen_genome is not None:
                pathogen_genomes.append(sample.uploaded_pathogen_genome)
            else:
                raise ValueError(
                    "Sample without sequencing reads collection nor uploaded"
                    " pathogen"
                )
        if len(pathogen_genomes) == 0:
            raise ValueError("No sequences selected for run.")

        if aligned_gisaid_dump_id is not None:
            aligned_gisaid_dump = (
                session.query(AlignedGisaidDump)
                .filter(AlignedGisaidDump.entity_id == aligned_gisaid_dump_id)
                .one()
            )
        else:
            aligned_gisaid_dump = (
                session.query(AlignedGisaidDump)
                .join(AlignedGisaidDump.producing_workflow)
                .order_by(Workflow.end_datetime.desc())
                .first()
            )

        workflow: PhyloRun = PhyloRun(
            start_datetime=datetime.datetime.now(),
            workflow_status=WorkflowStatusType.STARTED,
            software_versions={},
            group=group,
            # TODO: need build template / build args.
        )
        workflow.inputs = list(pathogen_genomes)
        workflow.inputs.append(aligned_gisaid_dump)
        workflow.template_file_path = (
            "workflows/setup_nextstrain_run/builds_template.yaml"
        )
        workflow.template_args = builds_template_args

        session.add(workflow)

        session.flush()
        print(workflow.workflow_id)
