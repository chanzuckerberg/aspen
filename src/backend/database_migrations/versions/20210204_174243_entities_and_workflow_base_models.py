"""entities and workflow base models

Create Date: 2021-02-04 17:42:44.236476

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210204_174243"
down_revision = "20210204_112248"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "entitytypes",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_entitytypes")),
        schema="aspen",
    )
    op.create_table(
        "workflowtypes",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_workflowtypes")),
        schema="aspen",
    )
    op.create_table(
        "entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_type", enumtables.enum_column.EnumType(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_type"],
            ["aspen.entitytypes.item_id"],
            name=op.f("fk_entities_entity_type_entitytypes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entities")),
        schema="aspen",
    )
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_type", enumtables.enum_column.EnumType(), nullable=False),
        sa.Column("run_date", sa.DateTime(), nullable=False),
        sa.Column(
            "software_versions",
            sa.JSON(),
            nullable=False,
            comment="A mapping between all the tools used in this workflow and the version used.",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_type"],
            ["aspen.workflowtypes.item_id"],
            name=op.f("fk_workflows_workflow_type_workflowtypes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflows")),
        schema="aspen",
    )
    op.create_table(
        "workflow_inputs",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_workflow_inputs_entity_id_entities"),
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_workflow_inputs_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint(
            "entity_id", "workflow_id", name=op.f("pk_workflow_inputs")
        ),
        schema="aspen",
    )
    op.create_table(
        "workflow_outputs",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_workflow_outputs_entity_id_entities"),
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_workflow_outputs_workflow_id_workflows"),
        ),
        sa.PrimaryKeyConstraint(
            "entity_id", "workflow_id", name=op.f("pk_workflow_outputs")
        ),
        schema="aspen",
    )
    op.enum_insert(
        "workflowtypes",
        [
            "FILTER_READ",
            "ALIGN_READ",
            "CALL_CONSENSUS",
            "PHYLO_RUN",
            "PROCESS_GISAID_DUMP",
        ],
        schema="aspen",
    )
    op.enum_insert(
        "entitytypes",
        [
            "RAW_GISAID_DUMP",
            "HOST_FILTERED_SEQUENCE",
            "SEQUENCING_READS",
            "PROCESSED_GISAID_DUMP",
            "BAM",
            "PATHOGEN_GENOME",
        ],
        schema="aspen",
    )


def downgrade():
    op.drop_table("workflow_outputs", schema="aspen")
    op.drop_table("workflow_inputs", schema="aspen")
    op.drop_table("workflows", schema="aspen")
    op.drop_table("entities", schema="aspen")
    op.drop_table("workflowtypes", schema="aspen")
    op.drop_table("entitytypes", schema="aspen")
