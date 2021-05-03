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
    AlignedGisaidDump,
    GisaidAlignmentWorkflow,
    ProcessedGisaidDump,
    WorkflowStatusType,
)
from aspen.database.models.workflow import SoftwareNames


@click.command("save")
@click.option("--aspen-workflow-rev", type=str, required=True)
@click.option("--aspen-creation-rev", type=str, required=True)
@click.option("--ncov-rev", type=str, required=True)
@click.option("--aspen-docker-image-version", type=str, required=True)
@click.option("--start-time", type=int, required=True)
@click.option("--end-time", type=int, required=True)
@click.option("--processed-gisaid-object-id", type=int, required=True)
@click.option("--gisaid-s3-bucket", type=str, required=True)
@click.option("--gisaid-sequences-s3-key", type=str, required=True)
@click.option("--gisaid-metadata-s3-key", type=str, required=True)
def cli(
    aspen_workflow_rev: str,
    aspen_creation_rev: str,
    ncov_rev: str,
    aspen_docker_image_version: str,
    start_time: int,
    end_time: int,
    processed_gisaid_object_id: int,
    gisaid_s3_bucket: str,
    gisaid_sequences_s3_key: str,
    gisaid_metadata_s3_key: str,
):
    start_time_datetime = datetime.datetime.fromtimestamp(start_time)
    end_time_datetime = datetime.datetime.fromtimestamp(end_time)

    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))
    with session_scope(interface) as session:
        processed_gisaid_dump: ProcessedGisaidDump = (
            session.query(ProcessedGisaidDump)
            .filter(ProcessedGisaidDump.id == processed_gisaid_object_id)
            .one()
        )

        # create an output
        aligned_gisaid_dump = AlignedGisaidDump(
            s3_bucket=gisaid_s3_bucket,
            sequences_s3_key=gisaid_sequences_s3_key,
            metadata_s3_key=gisaid_metadata_s3_key,
        )

        # attach a workflow
        workflow = GisaidAlignmentWorkflow(
            start_datetime=start_time_datetime,
            end_datetime=end_time_datetime,
            workflow_status=WorkflowStatusType.COMPLETED,
            software_versions={
                SoftwareNames.ASPEN_WORKFLOW: aspen_workflow_rev,
                SoftwareNames.ASPEN_CREATION: aspen_creation_rev,
                SoftwareNames.NCOV: ncov_rev,
                SoftwareNames.ASPEN_DOCKER_IMAGE: aspen_docker_image_version,
            },
        )

        workflow.inputs.append(processed_gisaid_dump)
        workflow.outputs.append(aligned_gisaid_dump)
        session.flush()
        print(aligned_gisaid_dump.entity_id)


if __name__ == "__main__":
    cli()
