import datetime

import click

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import (
    GisaidDumpWorkflow,
    ProcessedGisaidDump,
    RawGisaidDump,
    WorkflowStatusType,
)
from aspen.database.models.workflow import SoftwareNames


@click.command("save")
@click.option("--aspen-workflow-rev", type=str, required=True)
@click.option("--aspen-creation-rev", type=str, required=True)
@click.option("--ncov-ingest-rev", type=str, required=True)
@click.option("--start-time", type=int, required=True)
@click.option("--end-time", type=int, required=True)
@click.option("--raw-gisaid-object-id", type=int, required=True)
@click.option("--gisaid-s3-bucket", type=str, required=True)
@click.option("--gisaid-sequences-s3-key", type=str, required=True)
@click.option("--gisaid-metadata-s3-key", type=str, required=True)
def cli(
    aspen_workflow_rev: str,
    aspen_creation_rev: str,
    ncov_ingest_rev: str,
    start_time: int,
    end_time: int,
    raw_gisaid_object_id: int,
    gisaid_s3_bucket: str,
    gisaid_sequences_s3_key: str,
    gisaid_metadata_s3_key: str,
):
    start_time_datetime = datetime.datetime.fromtimestamp(start_time)
    end_time_datetime = datetime.datetime.fromtimestamp(end_time)

    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))
    with session_scope(interface) as session:
        raw_gisaid_dump: RawGisaidDump = (
            session.query(RawGisaidDump)
            .filter(RawGisaidDump.id == raw_gisaid_object_id)
            .one()
        )

        # create an output
        processed_gisaid_dump = ProcessedGisaidDump(
            s3_bucket=gisaid_s3_bucket,
            sequences_s3_key=gisaid_sequences_s3_key,
            metadata_s3_key=gisaid_metadata_s3_key,
        )

        # attach a workflow
        workflow = GisaidDumpWorkflow(
            start_datetime=start_time_datetime,
            end_datetime=end_time_datetime,
            workflow_status=WorkflowStatusType.COMPLETED,
            software_versions={
                SoftwareNames.ASPEN_WORKFLOW: aspen_workflow_rev,
                SoftwareNames.ASPEN_CREATION: aspen_creation_rev,
                SoftwareNames.NCOV_INGEST: ncov_ingest_rev,
            },
        )

        workflow.inputs.append(raw_gisaid_dump)
        workflow.outputs.append(processed_gisaid_dump)
        session.flush()
        print(processed_gisaid_dump.entity_id)


if __name__ == "__main__":
    cli()
