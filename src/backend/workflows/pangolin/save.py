from typing import Iterable, MutableSequence, Optional, Sequence, Type

import click
from sqlalchemy.orm import aliased, joinedload, undefer

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import (
    CalledPathogenGenome,
    Entity,
    HostFilteredSequencingReadsCollection,
    PathogenGenome,
    Sample,
    SequencingReadsCollection,
    UploadedPathogenGenome,
)

@click.command("save")
@click.option("pangolin_fh", "--pangolin-input-file", type=click.File("r"), required=True)
@click.option("--pangolin-version", type=str, required=True)
@click.option("--pangolin-last-updates", type=str, required=True)
def cli(
    pangolin_fh: io.TextIOBase
):
    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))

    with session_scope(interface) as session:
        


if __name__ == "__main__":
    cli(["--pangolin-input-file", "lineage_report.csv"])
    cli.save()