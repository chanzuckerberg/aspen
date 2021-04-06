import json
import os
from pathlib import Path
from typing import Type

import boto3
import click
from IPython.terminal.embed import InteractiveShellEmbed

from aspen import covidhub_import
from aspen.cli.toplevel import cli
from aspen.config.config import Config, RemoteDatabaseConfig
from aspen.config.development import DevelopmentConfig
from aspen.config.local import LocalConfig
from aspen.database.connection import enable_profiling, get_db_uri, init_db
from aspen.database.models import *  # noqa: F401, F403
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


@db.command("setup")
@click.option("--load-data", type=str, default=lambda: os.environ.get('DATA_LOAD_PATH', ''), help="S3 URI for data to import")
@click.pass_context
def setup(ctx, load_data):
    """If the database we're trying to connect to doesn't exist: create it and load a default dataset into it"""
    # TODO - we can move this to the top when https://github.com/kvesteri/sqlalchemy-utils/pull/506 is merged
    from sqlalchemy_utils import database_exists, create_database
    conf = ctx.obj["CONFIG"]
    engine = ctx.obj["ENGINE"]
    db_uri = conf.DATABASE_URI
    if database_exists(db_uri):
        print("Database already exists!")
        return

    print("Database does not exist, creating database")
    create_database(db_uri)
    if load_data:
        print(f"Importing {load_data}")
        import_data(load_data, db_uri)
    else:
        print(f"Creating empty tables")
        create_tables_and_schema(engine)


@db.command("create")
@click.pass_context
def create_db(ctx):
    create_tables_and_schema(ctx.obj["ENGINE"])


@db.command("drop")
@click.pass_context
def drop(ctx):
    # TODO - we can move this to the top when https://github.com/kvesteri/sqlalchemy-utils/pull/506 is merged
    from sqlalchemy_utils import database_exists, drop_database
    conf = ctx.obj["CONFIG"]
    db_uri = conf.DATABASE_URI
    if database_exists(db_uri):
        print("Database exists, dropping database")
        drop_database(db_uri)
    else:
        print("Database does not exist, skipping")
        exit(1)


def import_data(s3_path, db_uri):
    s3 = boto3.resource('s3')
    bucket_name = s3_path.split("/")[0]
    path = "/".join(s3_path.split("/")[1:])
    print(f"downloading {path}")
    s3.Bucket(bucket_name).download_file(path, 'db_data.sql')
    import subprocess
    with subprocess.Popen(["psql", db_uri], stdin=subprocess.PIPE) as proc:
        proc.stdin.write(open("db_data.sql", "rb").read())
        proc.stdin.close()



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
