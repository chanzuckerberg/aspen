"""add datatypes and can see tables

Create Date: 2021-02-04 11:09:58.589711

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210204_110958"
down_revision = "20210204_104338"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "datatypes",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_datatypes")),
        schema="aspen",
    )
    op.create_table(
        "can_see",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("viewer_group_id", sa.Integer(), nullable=False),
        sa.Column("owner_group_id", sa.Integer(), nullable=False),
        sa.Column("data_type", enumtables.enum_column.EnumType(), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_type"],
            ["aspen.datatypes.item_id"],
            name=op.f("fk_can_see_data_type_datatypes"),
        ),
        sa.ForeignKeyConstraint(
            ["owner_group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_can_see_owner_group_id_groups"),
        ),
        sa.ForeignKeyConstraint(
            ["viewer_group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_can_see_viewer_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_can_see")),
        schema="aspen",
    )
    op.enum_insert("datatypes", ["TREES", "SEQUENCES"], schema="aspen")


def downgrade():
    op.enum_delete("datatypes", ["TREES", "SEQUENCES"], schema="aspen")
    op.drop_table("can_see", schema="aspen")
    op.drop_table("datatypes", schema="aspen")
