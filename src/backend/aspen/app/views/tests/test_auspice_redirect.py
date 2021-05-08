import json

import requests

from aspen.database.models import CanSee, DataType
from aspen.test_infra.models.phylo_tree import phylorun_factory, phylotree_factory
from aspen.test_infra.models.sample import sample_factory
from aspen.test_infra.models.usergroup import group_factory, user_factory


def test_auspice_redirect_view(session, app, client, mock_s3_resource, test_data_dir):
    viewer_group = group_factory()
    can_see_group = group_factory("can_see")
    wrong_can_see_group = group_factory("wrong_can_see")
    no_can_see_group = group_factory("no_can_see")
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
        phylorun_factory(viewer_group),
        [local_sample, can_see_sample, wrong_can_see_sample, no_can_see_sample],
    )
    session.add(phylo_tree)
    session.commit()

    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    mock_s3_resource.create_bucket(Bucket=phylo_tree.s3_bucket)

    json_test_file = test_data_dir / "ncov_aspen.json"
    with json_test_file.open() as fh:
        test_json = json.dumps(json.load(fh))

    mock_s3_resource.Bucket(phylo_tree.s3_bucket).Object(phylo_tree.s3_key).put(
        Body=test_json
    )

    with client.session_transaction() as sess:
        sess["profile"] = {"name": user.name, "user_id": user.auth0_user_id}

    res = client.get(f"/api/auspice/view/{phylo_tree.id}")
    res_presigned = res.json["url"]

    # this is a little hacky, currently when calling a get request on moto generated presigned url it gets 404
    # i think this is due to calling get not being within the moto test scope, so as a workaround i''m checking that
    # the key and bucket names from the phylo tree entry are in the returned presigned url and that the response code from the view is 200
    assert res.status == "200 OK"
    assert app.aspen_config.EXTERNAL_AUSPICE_BUCKET in res_presigned

    tree = requests.get(res_presigned).json()
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
