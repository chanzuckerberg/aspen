"""add czb_failed_genome_recovery to Sample class

Create Date: 2021-04-16 19:58:54.716138

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210416_195853"
down_revision = "20210405_170924"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
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


def downgrade():
    op.drop_column("samples", "czb_failed_genome_recovery", schema="aspen")
