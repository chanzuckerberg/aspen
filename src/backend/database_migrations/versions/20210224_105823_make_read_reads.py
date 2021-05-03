"""make read -> reads

Create Date: 2021-02-24 10:58:25.108079

"""
import enumtables  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210224_105823"
down_revision = "20210222_220412"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table(
        "sequencing_read_collections",
        "sequencing_reads_collections",
        schema="aspen",
    )
    op.rename_table(
        "host_filtered_sequencing_read_collections",
        "host_filtered_sequencing_reads_collections",
        schema="aspen",
    )
    op.drop_constraint(
        "uq_host_filtered_sequencing_read_collections_s3_bucket",
        "host_filtered_sequencing_reads_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("uq_host_filtered_sequencing_reads_collections_s3_bucket"),
        "host_filtered_sequencing_reads_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.drop_constraint(
        "uq_sequencing_read_collections_s3_bucket",
        "sequencing_reads_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        op.f("uq_sequencing_reads_collections_s3_bucket"),
        "sequencing_reads_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )


def downgrade():
    op.drop_constraint(
        op.f("uq_sequencing_reads_collections_s3_bucket"),
        "sequencing_reads_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_sequencing_read_collections_s3_bucket",
        "sequencing_reads_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.drop_constraint(
        op.f("uq_host_filtered_sequencing_reads_collections_s3_bucket"),
        "host_filtered_sequencing_reads_collections",
        schema="aspen",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_host_filtered_sequencing_read_collections_s3_bucket",
        "host_filtered_sequencing_reads_collections",
        ["s3_bucket", "s3_key"],
        schema="aspen",
    )
    op.rename_table(
        "sequencing_reads_collections",
        "sequencing_read_collections",
        schema="aspen",
    )
    op.rename_table(
        "host_filtered_sequencing_reads_collections",
        "host_filtered_sequencing_read_collections",
        schema="aspen",
    )
