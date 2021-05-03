"""add workflow status, start/end times for workflows, and fix repository_type column

Create Date: 2021-02-25 16:22:54.468221

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20210225_162252"
down_revision = "20210218_211316"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workflow_status_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_workflow_status_types")),
        schema="aspen",
    )
    op.alter_column(
        "public_repository",
        "entity_type",
        new_column_name="repository_type",
        existing_type=enumtables.enum_column.EnumType(),
        existing_nullable=False,
        schema="aspen",
    )
    op.drop_constraint(
        "fk_public_repository_entity_type_public_repository_types",
        "public_repository",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_public_repository_repository_type_public_repository_types"),
        "public_repository",
        "public_repository_types",
        ["repository_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.add_column(
        "workflows",
        sa.Column(
            "end_datetime",
            sa.DateTime(),
            nullable=True,
            comment="datetime when the workflow is ended.  this is only valid when the workflow's status is COMPLETED.",
        ),
        schema="aspen",
    )
    op.add_column(
        "workflows",
        sa.Column(
            "start_datetime",
            sa.DateTime(),
            nullable=False,
            comment="datetime when the workflow is started.",
        ),
        schema="aspen",
    )
    op.add_column(
        "workflows",
        sa.Column(
            "workflow_status",
            enumtables.enum_column.EnumType(),
            nullable=False,
        ),
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_workflows_workflow_status_workflow_status_types"),
        "workflows",
        "workflow_status_types",
        ["workflow_status"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_column("workflows", "run_date", schema="aspen")
    op.enum_insert(
        "workflow_status_types",
        ["STARTED", "FAILED", "COMPLETED"],
        schema="aspen",
    )


def downgrade():
    op.add_column(
        "workflows",
        sa.Column(
            "run_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_workflows_workflow_status_workflow_status_types"),
        "workflows",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_column("workflows", "workflow_status", schema="aspen")
    op.drop_column("workflows", "start_datetime", schema="aspen")
    op.drop_column("workflows", "end_datetime", schema="aspen")
    op.alter_column(
        "public_repository",
        "repository_type",
        new_column_name="entity_type",
        existing_type=enumtables.enum_column.EnumType(),
        existing_nullable=False,
        schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_public_repository_repository_type_public_repository_types"),
        "public_repository",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_public_repository_entity_type_public_repository_types",
        "public_repository",
        "public_repository_types",
        ["entity_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_table("workflow_status_types", schema="aspen")
