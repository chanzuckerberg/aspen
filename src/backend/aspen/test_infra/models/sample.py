from datetime import datetime

from aspen.database.models import RegionType, Sample


def sample_factory(
    submitting_group,
    private_identifier="private_identifer",
    original_submission=None,
    public_identifier="public_identifier",
    collection_date=None,
    sample_collected_by="sample_collector",
    sample_collector_contact_address="sample_collector_address",
    location="Santa Clara County",
    division="California",
    country="USA",
    region=RegionType.NORTH_AMERICA,
    organism="SARS-CoV-2",
) -> Sample:
    original_submission = original_submission or {}
    collection_date = collection_date or datetime.now()
    return Sample(
        submitting_group=submitting_group,
        private_identifier=private_identifier,
        original_submission=original_submission,
        public_identifier=public_identifier,
        collection_date=collection_date,
        sample_collected_by=sample_collected_by,
        sample_collector_contact_address=sample_collector_contact_address,
        location=location,
        division=division,
        country=country,
        region=region,
        organism=organism,
    )
