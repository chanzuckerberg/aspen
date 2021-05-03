"""simplify accessions and add GENBANK

Create Date: 2021-02-25 18:01:56.487930

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210225_180155"
down_revision = "20210225_162252"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "uq_accessions_public_repository_id",
        "accessions",
        schema="aspen",
        type_="unique",
    )
    op.drop_constraint(
        "fk_accessions_public_repository_id_public_repository",
        "accessions",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_table("public_repository", schema="aspen")
    op.add_column(
        "accessions",
        sa.Column(
            "repository_type",
            enumtables.enum_column.EnumType(),
            nullable=False,
        ),
        schema="aspen",
    )
    op.create_unique_constraint(
        op.f("uq_accessions_repository_type"),
        "accessions",
        ["repository_type", "public_identifier"],
        schema="aspen",
    )
    op.create_foreign_key(
        op.f("fk_accessions_repository_type_public_repository_types"),
        "accessions",
        "public_repository_types",
        ["repository_type"],
        ["item_id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
    op.drop_column("accessions", "public_repository_id", schema="aspen")
    op.enum_insert("public_repository_types", ["GENBANK"], schema="aspen")


def downgrade():
    op.enum_delete("public_repository_types", ["GENBANK"], schema="aspen")
    op.add_column(
        "accessions",
        sa.Column(
            "public_repository_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        schema="aspen",
    )
    op.drop_constraint(
        op.f("fk_accessions_repository_type_public_repository_types"),
        "accessions",
        schema="aspen",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("uq_accessions_repository_type"),
        "accessions",
        schema="aspen",
        type_="unique",
    )
    op.drop_column("accessions", "repository_type", schema="aspen")
    op.create_table(
        "public_repository",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('aspen.public_repository_id_seq'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "repository_type",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("website", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["repository_type"],
            ["aspen.public_repository_types.item_id"],
            name="fk_public_repository_repository_type_public_repository_types",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_public_repository"),
        sa.UniqueConstraint("name", name="uq_public_repository_name"),
        sa.UniqueConstraint("website", name="uq_public_repository_website"),
        schema="aspen",
    )
    op.create_unique_constraint(
        "uq_accessions_public_repository_id",
        "accessions",
        ["public_repository_id", "public_identifier"],
        schema="aspen",
    )
    op.create_foreign_key(
        "fk_accessions_public_repository_id_public_repository",
        "accessions",
        "public_repository",
        ["public_repository_id"],
        ["id"],
        source_schema="aspen",
        referent_schema="aspen",
    )
