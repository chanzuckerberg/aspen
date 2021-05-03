"""use the leaf types for pathogen_genome

Create Date: 2021-02-10 12:55:54.816436

"""
import enumtables  # noqa: F401
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210210_125554"
down_revision = "20210210_132846"
branch_labels = None
depends_on = None


def upgrade():
    op.enum_insert(
        "entity_types",
        ["CALLED_PATHOGEN_GENOME", "UPLOADED_PATHOGEN_GENOME"],
        schema="aspen",
    )
    op.enum_delete("entity_types", ["PATHOGEN_GENOME"], schema="aspen")


def downgrade():
    op.enum_insert("['PATHOGEN_GENOME']", [], schema="entity_types")
    op.enum_delete(
        "entity_types",
        ["CALLED_PATHOGEN_GENOME", "UPLOADED_PATHOGEN_GENOME"],
        schema="aspen",
    )
