import urllib.request
from typing import Iterable
import subprocess

from sqlalchemy.orm import joinedload

from aspen.config.config import RemoteDatabaseConfig
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import Sample


def check_latest_pangolin_version() -> str:
    contents = urllib.request.urlopen(
        "https://github.com/cov-lineages/pangoLEARN/releases/latest"
    )
    # get latest version from redirected url:
    redirected_url: str = contents.url
    latest_version: str = redirected_url.split("/")[-1]
    return latest_version


def find_samples():
    interface: SqlAlchemyInterface = init_db(get_db_uri(RemoteDatabaseConfig()))
    most_recent_pango_version: str = check_latest_pangolin_version()

    with session_scope(interface) as session:
        # filter for sequences that were run with an older version of pangolin

        all_samples: Iterable[Sample] = session.query(Sample).options(
            joinedload(Sample.uploaded_pathogen_genome)
        )

        # TODO: update this comparison to be <= most_recent_pango_version
        # once we update this field to be a date instead of string

        samples_to_be_updated: Iterable[str] = [
            s.public_identifier
            for s in all_samples
            if (s.uploaded_pathogen_genome.pangolin_version is None)
            or (
                s.uploaded_pathogen_genome.pangolin_version != most_recent_pango_version
            )
        ]

        return samples_to_be_updated


if __name__ == "__main__":
    samples = find_samples()
    subprocess.run(["sh", "run_pangolin.sh"] + samples)

