from aspen.database.models import PhyloTree


def phylotree_factory(
    constituent_samples,
    bucket="test-bucket",
    key="test-key",
) -> PhyloTree:

    return PhyloTree(
        s3_bucket=bucket, s3_key=key, constituent_samples=constituent_samples
    )
