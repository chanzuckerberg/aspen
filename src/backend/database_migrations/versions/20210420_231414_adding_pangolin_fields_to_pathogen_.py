"""adding pangolin fields to pathogen_genome

Create Date: 2021-04-20 23:14:15.327852

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210420_231414"
down_revision = "20210416_195853"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pathogen_genomes",
        sa.Column("pangolin_last_updated", sa.DateTime(), nullable=True),
        schema="aspen",
    )
    op.add_column(
        "pathogen_genomes",
        sa.Column("pangolin_lineage", sa.String(), nullable=True),
        schema="aspen",
    )
    op.add_column(
        "pathogen_genomes",
        sa.Column("pangolin_probability", sa.Integer(), nullable=True),
        schema="aspen",
    )
    op.add_column(
        "pathogen_genomes",
        sa.Column("pangolin_version", sa.String(), nullable=True),
        schema="aspen",
    )


def downgrade():
    op.drop_column("pathogen_genomes", "pangolin_version", schema="aspen")
    op.drop_column("pathogen_genomes", "pangolin_probability", schema="aspen")
    op.drop_column("pathogen_genomes", "pangolin_lineage", schema="aspen")
    op.drop_column("pathogen_genomes", "pangolin_last_updated", schema="aspen")
