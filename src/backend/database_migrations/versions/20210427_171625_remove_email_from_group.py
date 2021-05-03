"""remove email from group

Create Date: 2021-04-27 17:16:27.347577

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210427_171625"
down_revision = "20210426_204155"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("uq_groups_email", "groups", schema="aspen", type_="unique")
    op.drop_column("groups", "email", schema="aspen")


def downgrade():
    op.add_column(
        "groups",
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False),
        schema="aspen",
    )
    op.create_unique_constraint("uq_groups_email", "groups", ["email"], schema="aspen")
