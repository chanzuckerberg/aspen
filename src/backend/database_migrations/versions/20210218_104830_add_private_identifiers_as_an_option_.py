"""add private identifiers as an option for cansee datatypes

Create Date: 2021-02-18 10:48:31.834354

"""
import enumtables  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210218_104830"
down_revision = "20210216_114729"
branch_labels = None
depends_on = None


def upgrade():
    op.enum_insert("data_types", ["PRIVATE_IDENTIFIERS"], schema="aspen")


def downgrade():
    op.enum_delete("data_types", ["PRIVATE_IDENTIFIERS"], schema="aspen")
