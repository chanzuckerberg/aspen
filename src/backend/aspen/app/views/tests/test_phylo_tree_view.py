import json
import random

from aspen.app.views.phylo_trees import PHYLO_TREE_KEY
from aspen.test_infra.models.phylo_tree import phylorun_factory, phylotree_factory
from aspen.test_infra.models.sample import sample_factory
from aspen.test_infra.models.sequences import uploaded_pathogen_genome_factory
from aspen.test_infra.models.usergroup import group_factory, user_factory


def test_phylo_tree_view(
    session,
    app,
    client,
    n_samples=5,
    n_trees=3,
):
    group = group_factory()
    user = user_factory(group)
    samples = [
        sample_factory(
            group,
            public_identifier=f"public_identifier_{ix}",
            private_identifier=f"private_identifier_{ix}",
        )
        for ix in range(n_samples)
    ]
    _ = [uploaded_pathogen_genome_factory(sample) for sample in samples]

    # make up to 3 trees, each with a random sample of uploaded pathogen genomes.
    trees = [
        phylotree_factory(
            phylorun_factory(group),
            random.sample(samples, k=random.randint(0, len(samples))),
            key=f"key_{ix}",
        )
        for ix in range(n_trees)
    ]
    session.add(group)
    session.commit()
    with client.session_transaction() as sess:
        sess["profile"] = {"name": user.name, "user_id": user.auth0_user_id}
    results = json.loads(client.get("/api/phylo_trees").get_data(as_text=True))

    for tree in trees:
        for result_tree in results[PHYLO_TREE_KEY]:
            if tree.entity_id == result_tree["phylo_tree_id"]:
                # found it!
                break
        else:
            raise ValueError(f"Could not find {tree} in results")

        assert result_tree["pathogen_genome_count"] == len(tree.constituent_samples)
