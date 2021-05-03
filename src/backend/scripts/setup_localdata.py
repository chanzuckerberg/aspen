from datetime import datetime

from aspen.config.local import LocalConfig
from aspen.database.connection import get_db_uri, init_db
from aspen.database.models import (
    Group,
    RegionType,
    Sample,
    SequencingInstrumentType,
    SequencingProtocolType,
    SequencingReadsCollection,
    User,
)


def create_test_group(session):
    g = session.query(Group).filter(Group.name == "CZI").one_or_none()
    if g:
        print("Group already exists")
        return g
    print("Creating group")
    g = Group(
        name="CZI",
        address="601 Marshall St, Redwood City, CA 94063",
    )
    session.add(g)
    session.commit()
    g = session.query(Group).filter(Group.name == "CZI").one_or_none()
    return g


def create_test_user(session, group):
    u = session.query(User).filter(User.auth0_user_id == "User1").one_or_none()
    if u:
        print("User already exists")
        return u
    print("Creating user")
    u = User(
        name="Test User",
        auth0_user_id="User1",
        email="aspen-testuser@chanzuckerberg.com",
        group_admin=True,
        system_admin=True,
        group=group,
    )
    session.add(u)
    return u


def create_sample(session, group):
    sample = (
        session.query(Sample).filter(Sample.submitting_group == group).one_or_none()
    )
    if sample:
        print("Sample already exists")
        return sample
    print("Creating sample")
    sample = Sample(
        submitting_group=group,
        private_identifier="private_identifer",
        original_submission={},
        public_identifier="public_identifier",
        collection_date=datetime.now(),
        sample_collected_by="sample_collector",
        sample_collector_contact_address="sample_collector_address",
        location="Santa Clara County",
        division="California",
        country="USA",
        region=RegionType.NORTH_AMERICA,
        organism="SARS-CoV-2",
    )
    session.add(sample)
    return sample


def create_sequencing_reads(session, sample):
    sequencing_reads = (
        session.query(SequencingReadsCollection)
        .filter(SequencingReadsCollection.sample == sample)
        .one_or_none()
    )
    if sequencing_reads:
        print("Sequencing Reads already exists")
        return sequencing_reads
    print("Creating Sequencing Reads")
    sequencing_reads = SequencingReadsCollection(
        sample=sample,
        sequencing_instrument=SequencingInstrumentType.ILLUMINA_GENOME_ANALYZER_IIX,
        sequencing_protocol=SequencingProtocolType.ARTIC_V3,
        sequencing_date=datetime.now(),
        s3_bucket="bucket",
        s3_key="key",
    )
    session.add(sequencing_reads)
    return sequencing_reads


def create_test_data(engine):
    session = engine.make_session()
    group = create_test_group(session)
    _ = create_test_user(session, group)
    sample = create_sample(session, group)
    _ = create_sequencing_reads(session, sample)
    session.commit()


def get_engine():
    config = LocalConfig()
    engine = init_db(get_db_uri(config))
    return engine


if __name__ == "__main__":
    engine = get_engine()
    create_test_data(engine)
