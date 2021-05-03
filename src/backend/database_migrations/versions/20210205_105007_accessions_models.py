"""accessions models

Create Date: 2021-02-05 10:50:08.345804

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210205_105007"
down_revision = "20210204_174243"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "publicrepositorytypes",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_publicrepositorytypes")),
        schema="aspen",
    )
    op.create_table(
        "public_repository",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_type", enumtables.enum_column.EnumType(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("website", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_type"],
            ["aspen.publicrepositorytypes.item_id"],
            name=op.f("fk_public_repository_entity_type_publicrepositorytypes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_public_repository")),
        sa.UniqueConstraint("name", name=op.f("uq_public_repository_name")),
        sa.UniqueConstraint("website", name=op.f("uq_public_repository_website")),
        schema="aspen",
    )
    op.create_table(
        "accessions",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("public_repository_id", sa.Integer(), nullable=False),
        sa.Column("public_identifier", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_accessions_entity_id_entities"),
        ),
        sa.ForeignKeyConstraint(
            ["public_repository_id"],
            ["aspen.public_repository.id"],
            name=op.f("fk_accessions_public_repository_id_public_repository"),
        ),
        sa.PrimaryKeyConstraint(
            "entity_id", "public_repository_id", name=op.f("pk_accessions")
        ),
        sa.UniqueConstraint(
            "public_repository_id",
            "public_identifier",
            name=op.f("uq_accessions_public_repository_id"),
        ),
        schema="aspen",
    )
    op.enum_insert("publicrepositorytypes", ["NCBI_SRA", "GISAID"], schema="aspen")


def downgrade():
    op.drop_table("accessions", schema="aspen")
    op.drop_table("public_repository", schema="aspen")
    op.drop_table("publicrepositorytypes", schema="aspen")
