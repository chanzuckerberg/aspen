"""add models for bam and workflows to and from bam

Create Date: 2021-02-12 10:59:51.519941

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210212_105950"
down_revision = "20210218_175604"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "align_read_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_align_read_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint("workflow_id", name=op.f("pk_align_read_workflows")),
        schema="aspen",
    )
    op.create_table(
        "call_consensus_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_call_consensus_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint(
            "workflow_id", name=op.f("pk_call_consensus_workflows")
        ),
        schema="aspen",
    )
    op.create_table(
        "bams",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.Column("sequencing_depth", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_bams_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_bams")),
        sa.UniqueConstraint("s3_bucket", "s3_key", name=op.f("uq_bams_s3_bucket")),
        schema="aspen",
    )


def downgrade():
    op.drop_table("bams", schema="aspen")
    op.drop_table("call_consensus_workflows", schema="aspen")
    op.drop_table("align_read_workflows", schema="aspen")
