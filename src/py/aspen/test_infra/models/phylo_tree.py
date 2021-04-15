from aspen.database.models import PhyloTree


def phylotree_factory(
        entity,
        s3_bucket="test_bucket",
        s3_key="test_tree",
        constituent_samples
):
