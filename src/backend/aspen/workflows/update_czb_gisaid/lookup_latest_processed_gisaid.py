import json

import click

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import ProcessedGisaidDump, Workflow, WorkflowStatusType


@click.command("lookup")
def cli():
    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))

    with session_scope(interface) as session:
        latest_processed_gisaid_dump: ProcessedGisaidDump = (
            session.query(ProcessedGisaidDump)
            .join(ProcessedGisaidDump.producing_workflow)
            .order_by(Workflow.end_datetime.desc())
            .filter(Workflow.workflow_status == WorkflowStatusType.COMPLETED)
            .limit(1)
            .one()
        )

        print(
            json.dumps(
                {
                    "bucket": latest_processed_gisaid_dump.s3_bucket,
                    "sequences_key": latest_processed_gisaid_dump.sequences_s3_key,
                    "metadata_key": latest_processed_gisaid_dump.metadata_s3_key,
                }
            )
        )


if __name__ == "__main__":
    cli()
