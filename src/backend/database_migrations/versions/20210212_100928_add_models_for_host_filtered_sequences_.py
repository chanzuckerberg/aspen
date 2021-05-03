"""add models for host filtered sequences and workflow

Create Date: 2021-02-12 10:09:29.296192

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210212_100928"
down_revision = "20210210_232422"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "filter_read_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_filter_read_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint("workflow_id", name=op.f("pk_filter_read_workflows")),
        schema="aspen",
    )
    op.create_table(
        "host_filtered_sequencing_reads",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_host_filtered_sequencing_reads_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint(
            "entity_id", name=op.f("pk_host_filtered_sequencing_reads")
        ),
        sa.UniqueConstraint(
            "s3_bucket",
            "s3_key",
            name=op.f("uq_host_filtered_sequencing_reads_s3_bucket"),
        ),
        schema="aspen",
    )
    op.enum_insert("entity_types", ["HOST_FILTERED_SEQUENCE_READS"], schema="aspen")
    op.enum_delete("entity_types", ["HOST_FILTERED_SEQUENCE"], schema="aspen")


def downgrade():
    op.enum_insert("['HOST_FILTERED_SEQUENCE']", [], schema="entity_types")
    op.enum_delete("entity_types", ["HOST_FILTERED_SEQUENCE_READS"], schema="aspen")
    op.drop_table("host_filtered_sequencing_reads", schema="aspen")
    op.drop_table("filter_read_workflows", schema="aspen")
