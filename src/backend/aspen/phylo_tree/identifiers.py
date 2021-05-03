from typing import Mapping, Optional, Set


def get_names_from_tree(tree) -> Set[str]:
    results: Set[str] = set()
    for node in tree:
        results.add(node["name"])
        if "children" in node:
            results.update(get_names_from_tree(node["children"]))

    return results


def rename_nodes_on_tree(
    tree: list,
    name_map: Mapping[str, str],
    save_key: Optional[str] = None,
) -> None:
    """Given a tree, a mapping of identifiers to their replacements, rename the nodes on
    the tree.  If `save_key` is provided, then the original identifier is saved using
    that as the key."""
    for node in tree:
        name = node["name"]
        renamed_value = name_map.get(name, None)
        if renamed_value is not None:
            # we found the replacement value! first, save the old value if the caller
            # requested.
            if save_key is not None:
                node[save_key] = name
            node["name"] = renamed_value
        if "children" in node:
            rename_nodes_on_tree(node["children"], name_map, save_key)
