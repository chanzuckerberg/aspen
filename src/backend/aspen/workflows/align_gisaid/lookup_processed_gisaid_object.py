import json

import click

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import ProcessedGisaidDump


@click.command("lookup")
@click.option("--processed-gisaid-object-id", type=int, required=True)
def cli(
    processed_gisaid_object_id: int,
):
    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))

    with session_scope(interface) as session:
        processed_gisaid_dump: ProcessedGisaidDump = (
            session.query(ProcessedGisaidDump)
            .filter(ProcessedGisaidDump.id == processed_gisaid_object_id)
            .one()
        )

        print(
            json.dumps(
                {
                    "bucket": processed_gisaid_dump.s3_bucket,
                    "sequences_key": processed_gisaid_dump.sequences_s3_key,
                    "metadata_key": processed_gisaid_dump.metadata_s3_key,
                }
            )
        )


if __name__ == "__main__":
    cli()
