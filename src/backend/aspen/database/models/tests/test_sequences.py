import pytest
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import undefer

from aspen.database.models.sequences import UploadedPathogenGenome
from aspen.test_infra.models.sample import sample_factory
from aspen.test_infra.models.sequences import sequencing_read_factory
from aspen.test_infra.models.usergroup import group_factory


def test_sequencing_reads(session):
    group = group_factory()
    sample = sample_factory(group)
    sequencing_reads = sequencing_read_factory(sample)

    session.add_all(
        (
            group,
            sample,
            sequencing_reads,
        )
    )
    session.flush()


def test_uploaded_pathogen_genome(session):
    group = group_factory()
    sample = sample_factory(group)
    uploaded_pathogen_genome = UploadedPathogenGenome(
        sample=sample,
        sequence="GAGAGACTCTCT",
        num_unambiguous_sites=8,
        num_missing_alleles=2,
        num_mixed=2,
    )

    session.add_all(
        (
            group,
            sample,
            uploaded_pathogen_genome,
        )
    )
    session.flush()

    # expire the data and try to implicitly load the sequence data.  it should fail.
    session.expire_all()
    uploaded_pathogen_genome = session.query(UploadedPathogenGenome).one()
    with pytest.raises(InvalidRequestError):
        uploaded_pathogen_genome.sequence

    # expire the data and try to explicitly load the sequence data.
    # it should succeed.
    session.expire_all()
    uploaded_pathogen_genome = (
        session.query(UploadedPathogenGenome)
        .options(undefer(UploadedPathogenGenome.sequence))
        .one()
    )
    uploaded_pathogen_genome.sequence
