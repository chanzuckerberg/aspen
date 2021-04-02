"""add relationship between PhyloTree and Sample; record extra metadata for PhyloRun

Create Date: 2021-04-01 21:19:17.198478

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20210401_211915"
down_revision = "20210330_120956"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "phylo_tree_samples",
        sa.Column("sample_id", sa.Integer(), nullable=False),
        sa.Column("phylo_tree_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["phylo_tree_id"],
            ["aspen.phylo_trees.entity_id"],
            name=op.f("fk_phylo_tree_samples_phylo_tree_id_phylo_trees"),
        ),
        sa.ForeignKeyConstraint(
            ["sample_id"],
            ["aspen.samples.id"],
            name=op.f("fk_phylo_tree_samples_sample_id_samples"),
        ),
        sa.PrimaryKeyConstraint(
            "sample_id", "phylo_tree_id", name=op.f("pk_phylo_tree_samples")
        ),
        schema="aspen",
    )
    op.add_column(
        "phylo_runs",
        sa.Column(
            "template_args",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        schema="aspen",
    )
    op.add_column(
        "phylo_runs",
        sa.Column("template_file_path", sa.String(), nullable=True),
        schema="aspen",
    )


def downgrade():
    op.drop_column("phylo_runs", "template_file_path", schema="aspen")
    op.drop_column("phylo_runs", "template_args", schema="aspen")
    op.drop_table("phylo_tree_samples", schema="aspen")
