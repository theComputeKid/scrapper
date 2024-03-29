import itertools, pathlib, json, os


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

    out: list[dict] = []
    for t in type_combos:
        my_type_combo_with_names = {}
        for idx, n in enumerate(names):
            my_type_combo_with_names[n] = t[idx]
        out.append(my_type_combo_with_names)
    return out


def get_includes(config: dict) -> str:
    if not "includes" in config:
        return ""
    incs = ""
    for inc in config["includes"]:
        incs += "#include " + inc + os.linesep
    return incs


def get_type_suffix_list(config: dict) -> str:
    user_list = {}
    if "mapping" in config:
        user_list = config["mapping"]

    my_current_directory = pathlib.Path(__file__).parents[1].resolve()
    json_file = my_current_directory / "utils" / "mapping.json"
    json_file_text = json.loads(json_file.read_text())

    out = json_file_text | user_list
    return out


def get_type_suffix(types: list[str], mapping: dict[str, str]) -> str:
    suffix = ""
    for t in types:
        if t in mapping:
            suffix += mapping[t] + "_"
        else:
            suffix += t + "_"
    return suffix[:-1]


def get_macro(config: dict) -> str:
    if "macro" in config:
        return config["macro"]
    else:
        return "SCRAPPER"
