"""schema changes for an explicit gisaid alignment workflow

Create Date: 2021-03-24 16:58:18.540682

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210324_165817"
down_revision = "20210323_135758"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "gisaid_alignment_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_gisaid_alignment_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint(
            "workflow_id", name=op.f("pk_gisaid_alignment_workflows")
        ),
        schema="aspen",
    )
    op.create_table(
        "aligned_gisaid_dump",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("sequences_s3_key", sa.String(), nullable=False),
        sa.Column("metadata_s3_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_aligned_gisaid_dump_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_aligned_gisaid_dump")),
        sa.UniqueConstraint(
            "s3_bucket",
            "metadata_s3_key",
            name="uq_aligned_gisaid_dump_s3_bucket_key",
        ),
        sa.UniqueConstraint(
            "s3_bucket",
            "sequences_s3_key",
            name="uq_aligned_gisaid_dump_s3_bucket_sequences",
        ),
        schema="aspen",
    )
    op.enum_insert("entity_types", ["ALIGNED_GISAID_DUMP"], schema="aspen")
    op.enum_insert("workflow_types", ["ALIGN_GISAID_DUMP"], schema="aspen")


def downgrade():
    op.enum_delete("workflow_types", ["ALIGN_GISAID_DUMP"], schema="aspen")
    op.enum_delete("entity_types", ["ALIGNED_GISAID_DUMP"], schema="aspen")
    op.drop_table("aligned_gisaid_dump", schema="aspen")
    op.drop_table("gisaid_alignment_workflows", schema="aspen")
