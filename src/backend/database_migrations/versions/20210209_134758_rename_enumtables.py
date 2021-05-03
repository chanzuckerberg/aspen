"""rename enumtables

Create Date: 2021-02-09 13:47:59.276384

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210209_134758"
down_revision = "20210205_105007"
branch_labels = None
depends_on = None


def upgrade():
    ####################################################################################
    # Create the new types tables.
    op.create_table(
        "data_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_data_types")),
        schema="aspen",
    )
    op.create_table(
        "entity_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_entity_types")),
        schema="aspen",
    )
    op.create_table(
        "public_repository_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_public_repository_types")),
        schema="aspen",
    )
    op.create_table(
        "workflow_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_workflow_types")),
        schema="aspen",
    )
    op.enum_insert(
        "entity_types",
        [
            "HOST_FILTERED_SEQUENCE",
            "BAM",
            "SEQUENCING_READS",
            "PROCESSED_GISAID_DUMP",
            "PATHOGEN_GENOME",
            "RAW_GISAID_DUMP",
        ],
        schema="aspen",
    )
    op.enum_insert("public_repository_types", ["GISAID", "NCBI_SRA"], schema="aspen")
    op.enum_insert("data_types", ["SEQUENCES", "TREES", "METADATA"], schema="aspen")
    op.enum_insert(
        "workflow_types",
        [
            "ALIGN_READ",
            "CALL_CONSENSUS",
            "PHYLO_RUN",
            "FILTER_READ",
            "PROCESS_GISAID_DUMP",
        ],
        schema="aspen",
    )

    ####################################################################################
    # Move the FK to the new types tables.
    op.drop_constraint(
        "fk_can_see_data_type_datatypes",
        "can_see",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_can_see_data_type_data_types"),
        "can_see",
        "data_types",
        ["data_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        "fk_entities_entity_type_entitytypes",
        "entities",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_entities_entity_type_entity_types"),
        "entities",
        "entity_types",
        ["entity_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        "fk_public_repository_entity_type_publicrepositorytypes",
        "public_repository",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_public_repository_entity_type_public_repository_types"),
        "public_repository",
        "public_repository_types",
        ["entity_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        "fk_workflows_workflow_type_workflowtypes",
        "workflows",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_workflows_workflow_type_workflow_types"),
        "workflows",
        "workflow_types",
        ["workflow_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )

    ####################################################################################
    # Drop the old types tables.
    op.drop_table("publicrepositorytypes", schema="aspen")
    op.drop_table("datatypes", schema="aspen")
    op.drop_table("entitytypes", schema="aspen")
    op.drop_table("workflowtypes", schema="aspen")


def downgrade():
    ####################################################################################
    # Create the old types tables.
    op.create_table(
        "workflowtypes",
        sa.Column("item_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("item_id", name="pk_workflowtypes"),
        schema="aspen",
    )
    op.create_table(
        "entitytypes",
        sa.Column("item_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("item_id", name="pk_entitytypes"),
        schema="aspen",
    )
    op.create_table(
        "datatypes",
        sa.Column("item_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("item_id", name="pk_datatypes"),
        schema="aspen",
    )
    op.create_table(
        "publicrepositorytypes",
        sa.Column("item_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("item_id", name="pk_publicrepositorytypes"),
        schema="aspen",
    )
    op.enum_insert(
        "entitytypes",
        [
            "HOST_FILTERED_SEQUENCE",
            "BAM",
            "SEQUENCING_READS",
            "PROCESSED_GISAID_DUMP",
            "PATHOGEN_GENOME",
            "RAW_GISAID_DUMP",
        ],
        schema="aspen",
    )
    op.enum_insert("publicrepositorytypes", ["GISAID", "NCBI_SRA"], schema="aspen")
    op.enum_insert("datatypes", ["SEQUENCES", "TREES", "METADATA"], schema="aspen")
    op.enum_insert(
        "workflowtypes",
        [
            "ALIGN_READ",
            "CALL_CONSENSUS",
            "PHYLO_RUN",
            "FILTER_READ",
            "PROCESS_GISAID_DUMP",
        ],
        schema="aspen",
    )

    ####################################################################################
    # Move the FK to the old types tables.
    op.drop_constraint(
        op.f("fk_workflows_workflow_type_workflow_types"),
        "workflows",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_workflows_workflow_type_workflowtypes",
        "workflows",
        "workflowtypes",
        ["workflow_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_public_repository_entity_type_public_repository_types"),
        "public_repository",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_public_repository_entity_type_publicrepositorytypes",
        "public_repository",
        "publicrepositorytypes",
        ["entity_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_entities_entity_type_entity_types"),
        "entities",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_entities_entity_type_entitytypes",
        "entities",
        "entitytypes",
        ["entity_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_can_see_data_type_data_types"),
        "can_see",
        schema="aspen",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_can_see_data_type_datatypes",
        "can_see",
        "datatypes",
        ["data_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )

    ####################################################################################
    # Drop the new types tables.
    op.drop_table("workflow_types", schema="aspen")
    op.drop_table("public_repository_types", schema="aspen")
    op.drop_table("entity_types", schema="aspen")
    op.drop_table("data_types", schema="aspen")
