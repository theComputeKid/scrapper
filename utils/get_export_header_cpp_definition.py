import utils, os


def __get_branch(func: dict, types: dict) -> str:
    out = "if constexpr("
    for t in types.keys():
        out += f"std::is_same_v<{types[t]}, {t}> && "
    out = out[:-4] + "){" + os.linesep
    out += f"\treturn {func['name']}_{utils.get_type_suffix(list(types.values()))}("
    for p in func["parameters"]:
        out += p["name"] + ", "
    out = out[:-2] + ");" + os.linesep
    out += "}"
    return out


def get_export_header_cpp_definition(func: dict) -> str:
    type_combos = utils.get_template_combinations(
        func["templates"], func["combination"]
    )
    out = utils.get_function_signature_cpp(func) + "{" + os.linesep
    for t in type_combos:
        out += __get_branch(func, t)
        out += os.linesep + "else "
    out += f'static_assert(!sizeof({func["templates"][0]["name"]}*), "Unsupported type for this function.");'
    out += os.linesep + "}"
    return out
