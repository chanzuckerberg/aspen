import io
from typing import Iterable, Sequence

import click
from sqlalchemy.orm import joinedload

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import Sample, UploadedPathogenGenome


@click.command("export")
@click.option("--sample-public-identifier", type=str, required=True, multiple=True)
@click.option("sequences_fh", "--sequences", type=click.File("w"), required=True)
def cli(sample_public_identifier: Sequence[str], sequences_fh: io.TextIOBase):
    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))

    with session_scope(interface) as session:
        all_samples: Iterable[Sample] = (
            session.query(Sample)
            .filter(Sample.public_identifier.in_(sample_public_identifier))
            .options(
                joinedload(Sample.uploaded_pathogen_genome).undefer(
                    UploadedPathogenGenome.sequence
                ),
            )
        )

        for sample in all_samples:
            pathogen_genome = sample.uploaded_pathogen_genome

            sequence: str = "".join(
                [
                    line
                    for line in pathogen_genome.sequence.splitlines()  # type: ignore
                    if not (line.startswith(">") or line.startswith(";"))
                ]
            )

            stripped_sequence: str = sequence.strip("Nn")
            sequences_fh.write(f">{pathogen_genome.entity_id}\n")  # type: ignore
            sequences_fh.write(stripped_sequence)


if __name__ == "__main__":
    cli()
