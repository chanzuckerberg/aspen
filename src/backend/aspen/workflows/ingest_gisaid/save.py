import datetime

import click

from aspen.config.config import Config
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import RawGisaidDump


@click.command("save")
@click.option("--aspen-workflow-rev", type=str, required=True)
@click.option("--aspen-creation-rev", type=str, required=True)
@click.option("--start-time", type=int, required=True)
@click.option("--end-time", type=int, required=True)
@click.option("--gisaid-s3-bucket", type=str, required=True)
@click.option("--gisaid-s3-key", type=str, required=True)
def cli(
    aspen_workflow_rev: str,
    aspen_creation_rev: str,
    start_time: int,
    end_time: int,
    gisaid_s3_bucket: str,
    gisaid_s3_key: str,
):
    start_time_datetime = datetime.datetime.fromtimestamp(start_time)

    interface: SqlAlchemyInterface = init_db(get_db_uri(Config()))

    entity = RawGisaidDump(
        download_date=start_time_datetime,
        s3_bucket=gisaid_s3_bucket,
        s3_key=gisaid_s3_key,
    )

    with session_scope(interface) as session:
        session.add(entity)
        session.flush()
        print(entity.entity_id)


if __name__ == "__main__":
    cli()
