"""processed gisaid dumps should have both a sequences and a metadata file

Create Date: 2021-03-23 13:58:00.002121

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210323_135758"
down_revision = "20210226_220143"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "processed_gisaid_dump",
        sa.Column("metadata_s3_key", sa.String(), nullable=False),
        schema="aspen",
    )
    op.add_column(
        "processed_gisaid_dump",
        sa.Column("sequences_s3_key", sa.String(), nullable=False),
        schema="aspen",
    )
    op.drop_constraint(
        "uq_processed_gisaid_dump_s3_bucket",
        "processed_gisaid_dump",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_processed_gisaid_dump_s3_bucket_key",
        "processed_gisaid_dump",
        ["s3_bucket", "metadata_s3_key"],
        schema="aspen",
    )
    op.create_unique_constraint(
        "uq_processed_gisaid_dump_s3_bucket_sequences",
        "processed_gisaid_dump",
        ["s3_bucket", "sequences_s3_key"],
        schema="aspen",
    )
    op.drop_column("processed_gisaid_dump", "s3_key", schema="aspen")


def downgrade():
    op.add_column(
        "processed_gisaid_dump",
        sa.Column("s3_key", sa.VARCHAR(), autoincrement=False, nullable=False),
        schema="aspen",
    )
    op.drop_constraint(
        "uq_processed_gisaid_dump_s3_bucket_sequences",
        "processed_gisaid_dump",
        schema="aspen",
        type_="unique",
    )
    op.drop_constraint(
        "uq_processed_gisaid_dump_s3_bucket_key",
        "processed_gisaid_dump",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_processed_gisaid_dump_s3_bucket",
        "processed_gisaid_dump",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.drop_column("processed_gisaid_dump", "sequences_s3_key", schema="aspen")
    op.drop_column("processed_gisaid_dump", "metadata_s3_key", schema="aspen")
