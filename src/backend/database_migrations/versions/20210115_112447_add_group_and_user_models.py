"""add group and user models

Create Date: 2021-01-15 11:24:48.165576

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210115_112447"
down_revision = "20210113_182045"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
        sa.UniqueConstraint("name", name=op.f("uq_groups_name")),
        sa.UniqueConstraint("email", name=op.f("uq_groups_email")),
        sa.UniqueConstraint("address", name=op.f("uq_groups_address")),
        schema="aspen",
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("auth0_user_id", sa.String(), nullable=False),
        sa.Column("group_admin", sa.Boolean(), nullable=False),
        sa.Column("system_admin", sa.Boolean(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["aspen.groups.id"],
            name=op.f("fk_users_group_id_groups"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("auth0_user_id", name=op.f("uq_users_auth0_user_id")),
        schema="aspen",
    )


def downgrade():
    op.drop_table("users", schema="aspen")
    op.drop_table("groups", schema="aspen")
