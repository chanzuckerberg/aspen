from datetime import datetime

from aspen.database.models import Entity, Workflow
from aspen.database.models.gisaid_dump import (
    GisaidDumpWorkflow,
    ProcessedGisaidDump,
    RawGisaidDump,
)
from aspen.database.models.workflow import WorkflowStatusType


def test_workflow(session):
    """Create a workflow that links a raw GISAID dump and a processed GISAID dump."""
    download_date = datetime.now()
    download_s3_bucket = "download_bucket"
    download_s3_key = "download_key"
    processed_s3_bucket = "processed_bucket"
    processed_sequences_s3_key = "processed_sequences_key"
    processed_metadata_s3_key = "processed_metadata_key"
    start_datetime = datetime.now()
    software_versions = {"test": "v0.0.1"}
    raw_gisaid_dump = RawGisaidDump(
        download_date=download_date,
        s3_bucket=download_s3_bucket,
        s3_key=download_s3_key,
    )

    processed_gisaid_dump = ProcessedGisaidDump(
        s3_bucket=processed_s3_bucket,
        sequences_s3_key=processed_sequences_s3_key,
        metadata_s3_key=processed_metadata_s3_key,
    )

    workflow = GisaidDumpWorkflow(
        start_datetime=start_datetime,
        workflow_status=WorkflowStatusType.STARTED,
        software_versions=software_versions,
        inputs=[raw_gisaid_dump],
        outputs=[processed_gisaid_dump],
    )

    session.add_all(
        (
            raw_gisaid_dump,
            processed_gisaid_dump,
            workflow,
        )
    )
    session.flush()

    all_entity_query = session.query(Entity)
    assert all_entity_query.count() == 2

    all_workflow_query = session.query(Workflow)
    assert all_workflow_query.count() == 1
    returned_workflow = all_workflow_query.one()
    assert isinstance(returned_workflow, GisaidDumpWorkflow)

    # check the inputs
    assert len(returned_workflow.inputs) == 1
    assert returned_workflow.inputs[0].id == raw_gisaid_dump.id
    assert len(returned_workflow.outputs) == 1
    assert returned_workflow.outputs[0].id == processed_gisaid_dump.id

    assert processed_gisaid_dump.raw_gisaid_dump == raw_gisaid_dump
    assert processed_gisaid_dump in raw_gisaid_dump.processed_gisaid_dumps
