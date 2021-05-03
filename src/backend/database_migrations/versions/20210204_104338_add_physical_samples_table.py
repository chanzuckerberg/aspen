"""add physical_samples table

Create Date: 2021-02-04 10:43:39.108565

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210204_104338"
down_revision = "20210115_112447"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "physical_samples",
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
        sa.Column("collection_date", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("division", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("purpose_of_sampling", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["submitting_group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_physical_samples_submitting_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_physical_samples")),
        sa.UniqueConstraint(
            "public_identifier",
            name=op.f("uq_physical_samples_public_identifier"),
        ),
        sa.UniqueConstraint(
            "submitting_group_id",
            "private_identifier",
            name=op.f("uq_physical_samples_submitting_group_id"),
        ),
        schema="aspen",
    )


def downgrade():
    op.drop_table("physical_samples", schema="aspen")
