import itertools


def get_template_combinations(templates: dict, method: str) -> list[dict]:
    names = []
    types = []
    for t in templates:
        names.append(t["name"])
        types.append(t["types"])

    if method == "all":
        type_combos = list(itertools.product(*types))
    elif method == "fixed":
        type_combos = list(zip(*types))
    else:
        raise ValueError(f"Unrecognized method provided: {method}")

    out: list[dict] = []
    for t in type_combos:
        my_type_combo_with_names = {}
        for idx, n in enumerate(names):
            my_type_combo_with_names[n] = t[idx]
        out.append(my_type_combo_with_names)
    return out
