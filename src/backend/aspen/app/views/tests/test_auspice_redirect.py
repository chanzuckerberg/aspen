import json

from aspen.test_infra.models.phylo_tree import phylotree_factory
from aspen.test_infra.models.sample import sample_factory
from aspen.test_infra.models.usergroup import group_factory, user_factory


def test_auspice_redirect_view(session, app, client, mock_s3_resource, test_data_dir):
    group = group_factory()
    session.add(group)
    session.commit()

    user = user_factory(group)

    sample_1 = sample_factory(
        group,
        private_identifier="private_identifer_1",
        public_identifier="public_identifier_1",
    )
    sample_2 = sample_factory(
        group,
        private_identifier="private_identifer_2",
        public_identifier="public_identifier_2",
    )

    session.add(sample_1)
    session.add(sample_2)
    session.commit()

    phylo_tree = phylotree_factory([sample_1, sample_2])
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
    assert phylo_tree.s3_bucket in res_presigned
    assert phylo_tree.s3_key in res_presigned
