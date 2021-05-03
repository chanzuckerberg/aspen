"""rename *sequencing_reads tables

Create Date: 2021-02-22 22:04:14.173048

"""
import enumtables  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210222_220412"
down_revision = "20210218_164249"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table(
        "sequencing_reads",
        "sequencing_read_collections",
        schema="aspen",
    )
    op.rename_table(
        "host_filtered_sequencing_reads",
        "host_filtered_sequencing_read_collections",
        schema="aspen",
    )
    op.drop_constraint(
        "uq_host_filtered_sequencing_reads_s3_bucket",
        "host_filtered_sequencing_read_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("uq_host_filtered_sequencing_read_collections_s3_bucket"),
        "host_filtered_sequencing_read_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.drop_constraint(
        "uq_sequencing_reads_s3_bucket",
        "sequencing_read_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("uq_sequencing_read_collections_s3_bucket"),
        "sequencing_read_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )


def downgrade():
    op.drop_constraint(
        op.f("uq_sequencing_read_collections_s3_bucket"),
        "sequencing_read_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_sequencing_reads_s3_bucket",
        "sequencing_read_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.drop_constraint(
        op.f("uq_host_filtered_sequencing_read_collections_s3_bucket"),
        "host_filtered_sequencing_read_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_host_filtered_sequencing_reads_s3_bucket",
        "host_filtered_sequencing_read_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.rename_table(
        "sequencing_read_collections",
        "sequencing_reads",
        schema="aspen",
    )
    op.rename_table(
        "host_filtered_sequencing_read_collections",
        "host_filtered_sequencing_reads",
        schema="aspen",
    )
