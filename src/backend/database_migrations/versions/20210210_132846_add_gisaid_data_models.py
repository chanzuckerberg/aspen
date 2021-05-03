"""add gisaid data models

Create Date: 2021-02-10 13:28:47.455763

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210210_132846"
down_revision = "20210209_134758"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "gisaid_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_gisaid_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint("workflow_id", name=op.f("pk_gisaid_workflows")),
        schema="aspen",
    )
    op.create_table(
        "processed_gisaid_dump",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_processed_gisaid_dump_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_processed_gisaid_dump")),
        sa.UniqueConstraint(
            "s3_bucket",
            "s3_key",
            name=op.f("uq_processed_gisaid_dump_s3_bucket"),
        ),
        schema="aspen",
    )
    op.create_table(
        "raw_gisaid_dump",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("download_date", sa.DateTime(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_raw_gisaid_dump_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_raw_gisaid_dump")),
        sa.UniqueConstraint(
            "s3_bucket", "s3_key", name=op.f("uq_raw_gisaid_dump_s3_bucket")
        ),
        schema="aspen",
    )


def downgrade():
    op.drop_table("raw_gisaid_dump", schema="aspen")
    op.drop_table("processed_gisaid_dump", schema="aspen")
    op.drop_table("gisaid_workflows", schema="aspen")
