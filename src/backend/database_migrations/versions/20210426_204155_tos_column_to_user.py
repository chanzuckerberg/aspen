"""tos column to user

Create Date: 2021-04-26 20:41:56.570401

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20210426_204155"
down_revision = "20210420_231414"
branch_labels = None
depends_on = None


def upgrade():

    # add new column to users as nullable
    op.add_column(
        "users",
        sa.Column("agreed_to_tos", sa.Boolean(), nullable=True),
        schema="aspen",
    )

    # set existing users agreed_to_tos column as false
    conn = op.get_bind()
    sql = sa.sql.text(
        "UPDATE aspen.users " "SET agreed_to_tos = false " "WHERE agreed_to_tos is NULL"
    )

    conn.execute(sql)

    # set agreed_to_tos to be non-nullable
    op.alter_column(
        "users",
        "agreed_to_tos",
        existing_type=postgresql.BOOLEAN(),
        nullable=False,
        schema="aspen",
    )


def downgrade():
    op.drop_column("users", "agreed_to_tos", schema="aspen")
