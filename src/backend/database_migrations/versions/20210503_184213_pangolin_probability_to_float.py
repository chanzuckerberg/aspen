"""pangolin probability to float

Create Date: 2021-05-03 18:42:14.746783

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210503_184213"
down_revision = "20210427_171625"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "pathogen_genomes",
        "pangolin_probability",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        schema="aspen",
    )


def downgrade():
    raise NotImplementedError("Downgrading the database is not allowed")
