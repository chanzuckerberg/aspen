"""update samples table

Create Date: 2021-02-18 11:07:11.896915

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20210218_110710"
down_revision = "20210216_114729"
branch_labels = None
depends_on = None


def upgrade():
    ####################################################################################
    # user/groups changes
    op.drop_constraint("uq_groups_address", "groups", schema="aspen", type_="unique")
    op.alter_column(
        "groups",
        "address",
        existing_type=sa.VARCHAR(),
        nullable=True,
        schema="aspen",
    )

    ####################################################################################
    # drop the old physical samples table and constraints.
    op.drop_constraint(
        "fk_sequencing_reads_physical_sample_id_physical_samples",
        "sequencing_reads",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_uploaded_pathogen_genomes_physical_sample_id_physica_4227",
        "uploaded_pathogen_genomes",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_table("physical_samples", schema="aspen")
    op.drop_column("sequencing_reads", "physical_sample_id", schema="aspen")
    op.drop_column("uploaded_pathogen_genomes", "physical_sample_id", schema="aspen")

    ####################################################################################
    # create the new samples table and constraints.
    op.create_table(
        "samples",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("submitting_group_id", sa.Integer(), nullable=False),
        sa.Column(
            "private_identifier",
            sa.String(),
            nullable=False,
            comment="This is the private identifier groups (DPHs) will use to map data back to their internal databases.",
        ),
        sa.Column(
            "original_submission",
            sa.JSON(),
            nullable=False,
            comment="This is the original metadata submitted by the user.",
        ),
        sa.Column(
            "public_identifier",
            sa.String(),
            nullable=False,
            comment="This is the public identifier we assign to this sample.",
        ),
        sa.Column("sample_collected_by", sa.String(), nullable=False),
        sa.Column("sample_collector_contact_email", sa.String(), nullable=True),
        sa.Column("sample_collector_contact_address", sa.String(), nullable=False),
        sa.Column(
            "authors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("collection_date", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("division", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("organism", sa.String(), nullable=False),
        sa.Column("host", sa.String(), nullable=True),
        sa.Column("purpose_of_sampling", sa.String(), nullable=True),
        sa.Column("specimen_processing", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["submitting_group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_samples_submitting_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_samples")),
        sa.UniqueConstraint(
            "public_identifier", name=op.f("uq_samples_public_identifier")
        ),
        sa.UniqueConstraint(
            "submitting_group_id",
            "private_identifier",
            name=op.f("uq_samples_submitting_group_id"),
        ),
        schema="aspen",
    )
    op.add_column(
        "uploaded_pathogen_genomes",
        sa.Column("sample_id", sa.Integer(), nullable=False),
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_uploaded_pathogen_genomes_sample_id_samples"),
        "uploaded_pathogen_genomes",
        "samples",
        ["sample_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.add_column(
        "sequencing_reads",
        sa.Column("sample_id", sa.Integer(), nullable=False),
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_sequencing_reads_sample_id_samples"),
        "sequencing_reads",
        "samples",
        ["sample_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )


def downgrade():
    ####################################################################################
    # user/groups changes
    op.create_unique_constraint(
        "uq_groups_address", "groups", ["address"], schema="aspen"
    )
    op.alter_column(
        "groups",
        "address",
        existing_type=sa.VARCHAR(),
        nullable=False,
        schema="aspen",
    )

    ####################################################################################
    # drop the new samples table and constraints.
    op.drop_constraint(
        op.f("fk_uploaded_pathogen_genomes_sample_id_samples"),
        "uploaded_pathogen_genomes",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("fk_sequencing_reads_sample_id_samples"),
        "sequencing_reads",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_table("samples", schema="aspen")
    op.drop_column("sequencing_reads", "sample_id", schema="aspen")
    op.drop_column("uploaded_pathogen_genomes", "sample_id", schema="aspen")

    ####################################################################################
    # create the old physical samples table and constraints.
    op.create_table(
        "physical_samples",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('aspen.physical_samples_id_seq'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "submitting_group_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "private_identifier",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
            comment="This is the private identifier groups (DPHs) will use to map data back to their internal databases.",
        ),
        sa.Column(
            "original_submission",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
            comment="This is the original metadata submitted by the user.",
        ),
        sa.Column(
            "public_identifier",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
            comment="This is the public identifier we assign to this sample.",
        ),
        sa.Column(
            "collection_date",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("location", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("division", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("country", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "purpose_of_sampling",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["submitting_group_id"],
            ["aspen.groups.id"],
            name="fk_physical_samples_submitting_group_id_groups",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_physical_samples"),
        sa.UniqueConstraint(
            "public_identifier", name="uq_physical_samples_public_identifier"
        ),
        sa.UniqueConstraint(
            "submitting_group_id",
            "private_identifier",
            name="uq_physical_samples_submitting_group_id",
        ),
        schema="aspen",
    )
    op.add_column(
        "uploaded_pathogen_genomes",
        sa.Column(
            "physical_sample_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        schema="aspen",
    )
    op.create_foreign_key(
        "fk_uploaded_pathogen_genomes_physical_sample_id_physica_4227",
        "uploaded_pathogen_genomes",
        "physical_samples",
        ["physical_sample_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.add_column(
        "sequencing_reads",
        sa.Column(
            "physical_sample_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        schema="aspen",
    )
    op.create_foreign_key(
        "fk_sequencing_reads_physical_sample_id_physical_samples",
        "sequencing_reads",
        "physical_samples",
        ["physical_sample_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
