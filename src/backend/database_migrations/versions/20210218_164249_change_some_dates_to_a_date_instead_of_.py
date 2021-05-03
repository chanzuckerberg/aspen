"""change some dates to a date instead of a datetime

Create Date: 2021-02-18 16:42:50.891582

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210218_164249"
down_revision = "20210212_105950"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "samples",
        "collection_date",
        type_=sa.DATE(),
        schema="aspen",
    )
    op.alter_column(
        "sequencing_reads",
        "sequencing_date",
        type_=sa.DATE(),
        schema="aspen",
    )


def downgrade():
    op.alter_column(
        "samples",
        "collection_date",
        type_=sa.DATETIME(),
        schema="aspen",
    )
    op.alter_column(
        "sequencing_reads",
        "sequencing_date",
        type_=sa.DATETIME(),
        schema="aspen",
    )
