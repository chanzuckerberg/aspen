"""accessions to workflow model

Create Date: 2021-03-30 12:09:58.581873

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20210330_120956"
down_revision = "20210324_165817"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM aspen.accessions")

    op.create_table(
        "accession_workflows",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_accession_workflows_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint("workflow_id", name=op.f("pk_accession_workflows")),
        schema="aspen",
    )
    op.drop_column("accessions", "id", schema="aspen")
    op.alter_column(
        "workflows",
        "start_datetime",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_comment="datetime when the workflow is started.",
        schema="aspen",
    )
    op.enum_insert("entity_types", ["PUBLIC_REPOSITORY_SUBMISSION"], schema="aspen")
    op.enum_insert("workflow_types", ["PUBLIC_REPOSITORY_SUBMISSION"], schema="aspen")


def downgrade():
    raise NotImplementedError("Reversing this migration is not supported")
