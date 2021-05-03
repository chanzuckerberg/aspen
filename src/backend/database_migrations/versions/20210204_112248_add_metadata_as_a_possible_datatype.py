"""add METADATA as a possible datatype

Create Date: 2021-02-04 11:22:49.102647

"""
import enumtables  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210204_112248"
down_revision = "20210204_110958"
branch_labels = None
depends_on = None


def upgrade():
    op.enum_insert("datatypes", ["METADATA"], schema="aspen")


def downgrade():
    op.enum_delete("datatypes", ["METADATA"], schema="aspen")
