"""update the relationship between entities and workflows

Create Date: 2021-02-10 23:24:23.837672

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210210_232422"
down_revision = "20210210_134341"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("workflow_outputs", schema="aspen")
    op.add_column(
        "entities",
        sa.Column("producing_workflow_id", sa.Integer(), nullable=True),
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_entities_producing_workflow_id_workflows"),
        "entities",
        "workflows",
        ["producing_workflow_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_entities_producing_workflow_id_workflows"),
        "entities",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_column("entities", "producing_workflow_id", schema="aspen")
    op.create_table(
        "workflow_outputs",
        sa.Column("entity_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("workflow_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name="fk_workflow_outputs_entity_id_entities",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name="fk_workflow_outputs_workflow_id_workflows",
        ),
        sa.PrimaryKeyConstraint("entity_id", "workflow_id", name="pk_workflow_outputs"),
        schema="aspen",
    )
