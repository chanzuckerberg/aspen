"""add a created_date to SequencingReadsCollections and UploadedPathogenGenome

Create Date: 2021-02-25 22:11:26.891372

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210225_221125"
down_revision = "20210225_162252"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sequencing_reads_collections",
        sa.Column(
            "upload_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="aspen",
    )
    op.add_column(
        "uploaded_pathogen_genomes",
        sa.Column(
            "upload_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema="aspen",
    )


def downgrade():
    op.drop_column("uploaded_pathogen_genomes", "upload_date", schema="aspen")
    op.drop_column("sequencing_reads_collections", "upload_date", schema="aspen")
