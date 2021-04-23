import json

from aspen.app.views.phylo_trees import _process_phylo_tree
from aspen.database.models import CanSee, DataType
from aspen.test_infra.models.phylo_tree import phylotree_factory
from aspen.test_infra.models.sample import sample_factory
from aspen.test_infra.models.usergroup import group_factory, user_factory


def test_phylo_tree_rename(session, mock_s3_resource, test_data_dir):
    """Create a set of samples belonging to different groups with different levels of
    can-see relationships.  Rename the nodes according to the can-see rules, and verify
    that the nodes are renamed correctly."""
    viewer_group = group_factory()
    can_see_group = group_factory("can_see", email="can_see@yahoo.com")
    wrong_can_see_group = group_factory(
        "wrong_can_see", email="wrong_can_see@hotmail.com"
    )
    no_can_see_group = group_factory("no_can_see", email="no_can_see@aol.com")
    can_see_group.can_be_seen_by.append(
        CanSee(
            viewer_group=viewer_group,
            owner_group=can_see_group,
            data_type=DataType.PRIVATE_IDENTIFIERS,
        )
    )
    wrong_can_see_group.can_be_seen_by.append(
        CanSee(
            viewer_group=viewer_group,
            owner_group=wrong_can_see_group,
            data_type=DataType.SEQUENCES,
        )
    )
    session.add_all(
        [viewer_group, can_see_group, wrong_can_see_group, no_can_see_group]
    )

    user = user_factory(viewer_group)

    local_sample = sample_factory(
        viewer_group,
        private_identifier="private_identifier_1",
        public_identifier="public_identifier_1",
    )
    can_see_sample = sample_factory(
        can_see_group,
        private_identifier="private_identifier_2",
        public_identifier="public_identifier_2",
    )
    wrong_can_see_sample = sample_factory(
        wrong_can_see_group,
        private_identifier="private_identifer_3",
        public_identifier="public_identifier_3",
    )
    no_can_see_sample = sample_factory(
        no_can_see_group,
        private_identifier="private_identifer_4",
        public_identifier="public_identifier_4",
    )

    phylo_tree = phylotree_factory(
        [local_sample, can_see_sample, wrong_can_see_sample, no_can_see_sample]
    )

    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    mock_s3_resource.create_bucket(Bucket=phylo_tree.s3_bucket)

    json_test_file = test_data_dir / "ncov_aspen.json"
    with json_test_file.open() as fh:
        test_json = json.dumps(json.load(fh))

    mock_s3_resource.Bucket(phylo_tree.s3_bucket).Object(phylo_tree.s3_key).put(
        Body=test_json
    )

    # this is mandatory because we use an id to reference the tree.
    session.commit()

    tree = _process_phylo_tree(session, phylo_tree.entity_id, user.auth0_user_id)

    assert tree == {
        "tree": {
            "name": "private_identifier_1",
            "GISAID_ID": "public_identifier_1",
            "children": [
                {"name": "private_identifier_2", "GISAID_ID": "public_identifier_2"},
                {"name": "public_identifier_3"},
                {
                    "name": "public_identifier_4",
                    "children": [{"name": "public_identifier_5"}],
                },
            ],
        }
    }
