"""fix default for czb_failed_genome_recovery

Create Date: 2021-05-08 00:01:31.031934

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210508_000129"
down_revision = "20210503_184213"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "samples",
        sa.Column(
            "czb_failed_genome_recovery",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment=(
                "This is set to true iff this is sample sequenced by CZB and failed"
                " genome recovery.",
            ),
        ),
        schema="aspen",
    )
    op.execute(
        """
        UPDATE aspen.samples
          SET czb_failed_genome_recovery=FALSE
          WHERE
              samples.id IN (
                SELECT sample_id FROM aspen.uploaded_pathogen_genomes
              )
            OR
              samples.id IN (
                SELECT sample_id FROM aspen.sequencing_reads_collections
              )
        """
    )


def downgrade():
    op.alter_column(
        "samples",
        sa.Column(
            "czb_failed_genome_recovery",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
            comment="This is set to true iff this is sample sequenced by CZB and failed genome recovery.",
        ),
        schema="aspen",
    )
