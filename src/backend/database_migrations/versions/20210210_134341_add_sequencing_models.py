"""add sequencing models

Create Date: 2021-02-10 13:43:41.883956

"""
import enumtables  # noqa: F401
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20210210_134341"
down_revision = "20210210_125554"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sequencing_instrument_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_sequencing_instrument_types")),
        schema="aspen",
    )
    op.create_table(
        "sequencing_protocol_types",
        sa.Column("item_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("item_id", name=op.f("pk_sequencing_protocol_types")),
        schema="aspen",
    )
    op.create_table(
        "pathogen_genomes",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.String(), nullable=False),
        sa.Column("num_unambiguous_sites", sa.Integer(), nullable=False),
        sa.Column("num_n", sa.Integer(), nullable=False),
        sa.Column("num_mixed", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_pathogen_genomes_entity_id_entities"),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_pathogen_genomes")),
        schema="aspen",
    )
    op.create_table(
        "sequencing_reads",
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("physical_sample_id", sa.Integer(), nullable=False),
        sa.Column(
            "sequencing_instrument",
            enumtables.enum_column.EnumType(),
            nullable=False,
        ),
        sa.Column(
            "sequencing_protocol",
            enumtables.enum_column.EnumType(),
            nullable=False,
        ),
        sa.Column("s3_bucket", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.Column("sequencing_date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["aspen.entities.id"],
            name=op.f("fk_sequencing_reads_entity_id_entities"),
        ),
        sa.ForeignKeyConstraint(
            ["physical_sample_id"],
            ["aspen.physical_samples.id"],
            name=op.f("fk_sequencing_reads_physical_sample_id_physical_samples"),
        ),
        sa.ForeignKeyConstraint(
            ["sequencing_instrument"],
            ["aspen.sequencing_instrument_types.item_id"],
            name=op.f(
                "fk_sequencing_reads_sequencing_instrument_sequencing_instrument_types"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["sequencing_protocol"],
            ["aspen.sequencing_protocol_types.item_id"],
            name=op.f(
                "fk_sequencing_reads_sequencing_protocol_sequencing_protocol_types"
            ),
        ),
        sa.PrimaryKeyConstraint("entity_id", name=op.f("pk_sequencing_reads")),
        sa.UniqueConstraint(
            "s3_bucket", "s3_key", name=op.f("uq_sequencing_reads_s3_bucket")
        ),
        schema="aspen",
    )
    op.create_table(
        "called_pathogen_genomes",
        sa.Column("pathogen_genome_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["pathogen_genome_id"],
            ["aspen.pathogen_genomes.entity_id"],
            name=op.f("fk_called_pathogen_genomes_pathogen_genome_id_pathogen_genomes"),
        ),
        sa.PrimaryKeyConstraint(
            "pathogen_genome_id", name=op.f("pk_called_pathogen_genomes")
        ),
        schema="aspen",
    )
    op.create_table(
        "uploaded_pathogen_genomes",
        sa.Column("pathogen_genome_id", sa.Integer(), nullable=False),
        sa.Column("physical_sample_id", sa.Integer(), nullable=False),
        sa.Column("sequencing_depth", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["pathogen_genome_id"],
            ["aspen.pathogen_genomes.entity_id"],
            name=op.f(
                "fk_uploaded_pathogen_genomes_pathogen_genome_id_pathogen_genomes"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["physical_sample_id"],
            ["aspen.physical_samples.id"],
            name=op.f(
                "fk_uploaded_pathogen_genomes_physical_sample_id_physical_samples"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "pathogen_genome_id", name=op.f("pk_uploaded_pathogen_genomes")
        ),
        schema="aspen",
    )
    op.enum_insert(
        "sequencing_instrument_types",
        [
            "Illumina HiSeq X",
            "DNBSEQ-G50",
            "Illumina Genome Analyzer II",
            "DNBSEQ-G400 FAST",
            "Illumina Genome Analyzer",
            "PacBio Sequel II",
            "Ion Torrent S5",
            "Oxford Nanopore PromethION",
            "Ion Torrent PGM",
            "Illumina MiSeq",
            "Missing",
            "Illumina NextSeq 500",
            "DNBSEQ-G400",
            "Not Applicable",
            "Not Collected",
            "Not Provided",
            "Illumina NovaSeq 6000",
            "Illumina MiniSeq",
            "PacBio RS",
            "Oxford Nanopore GridION",
            "Illumina HiSeq 3000",
            "Illumina NextSeq 550",
            "PacBio Sequel",
            "Ion Torrent Proton",
            "Illumina HiSeq X Five",
            "Illumina iSeq 100",
            "Illumina Genome Analyzer IIx",
            "Oxford Nanopore MinION",
            "Illumina HiSeq 2000",
            "BGISEQ-500",
            "PacBio RS II",
            "Illumina HiSeq 4000",
            "Illumina HiScanSQ",
            "Ion Torrent S5 XL",
            "Illumina HiSeq X Ten",
            "Illumina HiSeq 1500",
            "Illumina HiSeq 2500",
            "Illumina HiSeq 1000",
            "DNBSEQ-T7",
            "Restricted Access",
        ],
        schema="aspen",
    )
    op.enum_insert("sequencing_protocol_types", ["artic_v3"], schema="aspen")


def downgrade():
    op.drop_table("uploaded_pathogen_genomes", schema="aspen")
    op.drop_table("called_pathogen_genomes", schema="aspen")
    op.drop_table("sequencing_reads", schema="aspen")
    op.drop_table("pathogen_genomes", schema="aspen")
    op.drop_table("sequencing_protocol_types", schema="aspen")
    op.drop_table("sequencing_instrument_types", schema="aspen")
