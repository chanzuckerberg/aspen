"""add phylo run objects

Create Date: 2021-02-26 22:01:44.945281

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210226_220143"
down_revision = "20210226_092430"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "phylo_runs",
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["aspen.workflows.id"],
            name=op.f("fk_phylo_runs_workflow_id_workflows"),
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_phylo_runs_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("workflow_id", name=op.f("pk_phylo_runs")),
        schema="aspen",
    )
    op.create_table(
        "phylo_trees",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_phylo_trees_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_phylo_trees")),
        sa.UniqueConstraint(
            "s3_bucket", "s3_key", name=op.f("uq_phylo_trees_s3_bucket")
        ),
        schema="aspen",
    )
    op.enum_insert("entity_types", ["PHYLO_TREE"], schema="aspen")


def downgrade():
    op.drop_table("phylo_trees", schema="aspen")
    op.execute("""DELETE FROM aspen.entities WHERE entity_type='PHYLO_TREE'""")
    op.drop_table("phylo_runs", schema="aspen")
    op.enum_delete("entity_types", ["PHYLO_TREE"], schema="aspen")
