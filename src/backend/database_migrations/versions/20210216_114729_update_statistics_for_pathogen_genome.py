"""update statistics for pathogen genome

Create Date: 2021-02-16 11:47:30.766109

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210216_114729"
down_revision = "20210212_100928"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "pathogen_genomes",
        "num_n",
        new_column_name="num_missing_alleles",
        existing_type=sa.INTEGER(),
        comment="Number of sites with N, the missing allele, typically indicating low depth",
        existing_nullable=False,
        schema="aspen",
    )
    op.alter_column(
        "pathogen_genomes",
        "num_mixed",
        existing_type=sa.INTEGER(),
        comment="Number of sites with an ambiguous allele, e.g. M, K, Y, etc., indicating support for 2 or more alleles in the reads.",
        existing_nullable=False,
        schema="aspen",
    )
    op.alter_column(
        "pathogen_genomes",
        "num_unambiguous_sites",
        existing_type=sa.INTEGER(),
        comment="Number of sites with allele A, C, T, or G",
        existing_nullable=False,
        schema="aspen",
    )


def downgrade():
    op.alter_column(
        "pathogen_genomes",
        "num_missing_alleles",
        new_column_name="num_n",
        existing_type=sa.INTEGER(),
        comment=None,
        existing_comment="Number of sites with N, the missing allele, typically indicating low depth",
        existing_nullable=False,
        schema="aspen",
    )
    op.alter_column(
        "pathogen_genomes",
        "num_unambiguous_sites",
        existing_type=sa.INTEGER(),
        comment=None,
        existing_comment="Number of sites with allele A, C, T, or G",
        existing_nullable=False,
        schema="aspen",
    )
    op.alter_column(
        "pathogen_genomes",
        "num_mixed",
        existing_type=sa.INTEGER(),
        comment=None,
        existing_comment="Number of sites with an ambiguous allele, e.g. M, K, Y, etc., indicating support for 2 or more alleles in the reads.",
        existing_nullable=False,
        schema="aspen",
    )
