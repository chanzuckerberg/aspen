"""fix accessions, sequencing_reads, and uploaded_pathogen_genome

Create Date: 2021-02-18 21:13:17.850532

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210218_211316"
down_revision = "20210224_105823"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        op.f("pk_accessions"),
        "accessions",
        schema="aspen",
        type_="primary",
    )
    op.add_column(
        "accessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        schema="aspen",
    )
    op.create_primary_key(
        op.f("pk_accessions"),
        "accessions",
        ["id"],
        schema="aspen",
    )
    op.create_unique_constraint(
        op.f("uq_sequencing_reads_collections_sample_id"),
        "sequencing_reads_collections",
        ["sample_id"],
        schema="aspen",
    )
    op.create_unique_constraint(
        op.f("uq_uploaded_pathogen_genomes_sample_id"),
        "uploaded_pathogen_genomes",
        ["sample_id"],
        schema="aspen",
    )


def downgrade():
    op.drop_constraint(
        op.f("uq_uploaded_pathogen_genomes_sample_id"),
        "uploaded_pathogen_genomes",
        schema="aspen",
        type_="unique",
    )
    op.drop_constraint(
        op.f("uq_sequencing_reads_collections_sample_id"),
        "sequencing_reads_collections",
        schema="aspen",
        type_="unique",
    )
    op.drop_constraint(
        op.f("pk_accessions"),
        "accessions",
        schema="aspen",
        type_="primary",
    )
    op.drop_column("accessions", "id", schema="aspen")
    op.create_primary_key(
        op.f("pk_accessions"),
        "accessions",
        ["entity_id", "public_repository_id"],
        schema="aspen",
    )
