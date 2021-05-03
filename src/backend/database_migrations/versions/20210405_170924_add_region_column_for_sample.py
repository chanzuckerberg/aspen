"""add region column for sample

Create Date: 2021-04-05 17:09:26.078925

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210405_170924"
down_revision = "20210401_211915"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "region_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_region_types")),
        schema="aspen",
    )
    op.enum_insert(
        "region_types",
        [
            "North America",
            "Oceania",
            "Asia",
            "Europe",
            "South America",
            "Africa",
        ],
        schema="aspen",
    )
    op.add_column(
        "samples",
        sa.Column(
            "region",
            sa.String(),
            nullable=True,
            comment="This is the continent this sample was collected from.",
        ),
        schema="aspen",
    )
    op.execute("""UPDATE aspen.samples SET region='North America'""")
    op.alter_column(
        "samples",
        "region",
        existing_type=sa.VARCHAR(),
        nullable=False,
        existing_comment="This is the continent this sample was collected from.",
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_samples_region_region_types"),
        "samples",
        "region_types",
        ["region"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )


def downgrade():
    op.drop_constraint(
        op.f("fk_samples_region_region_types"),
        "samples",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_column("samples", "region", schema="aspen")
    op.drop_table("region_types", schema="aspen")
