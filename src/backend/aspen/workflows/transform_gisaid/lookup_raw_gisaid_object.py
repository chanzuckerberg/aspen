import json

import click

from aspen.config.config import Config
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import RawGisaidDump


@click.command("lookup")
@click.option("--raw-gisaid-object-id", type=int, required=True)
def cli(
    raw_gisaid_object_id: int,
):
    interface: SqlAlchemyInterface = init_db(get_db_uri(Config()))

    with session_scope(interface) as session:
        raw_gisaid_dump: RawGisaidDump = (
            session.query(RawGisaidDump)
            .filter(RawGisaidDump.id == raw_gisaid_object_id)
            .one()
        )

        print(
            json.dumps(
                {
                    "bucket": raw_gisaid_dump.s3_bucket,
                    "key": raw_gisaid_dump.s3_key,
                }
            )
        )


if __name__ == "__main__":
    cli()
