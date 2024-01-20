import utils


def __get_type(arg: dict, templates: str) -> str:
    if arg["type"] in templates:
        t = templates[arg["type"]]
    else:
        t = arg["type"]
    if arg["const"]:
        t += " const"
    if arg["pointer"]:
        t += "*"
    return t


def get_function_signature_c(
    func: dict, templates: dict, mapping: dict[str, str]
) -> str:
    """Generates a C function signature.

    The configuration is read from a "function" object obtained from the validated config JSON file.

    Parameters
    ----------
    func : dict
        "function" object obtained from the validated config JSON file.

    templates : dict
        Templates used in the C++ function for which this wrapper is being generated for.
        E.g.: {"T1": "float", "T2": "double"}
    """
    decl = __get_type(func["return"], templates) + " "
    decl += (
        func["name"] + "_" + utils.get_type_suffix(list(templates.values()), mapping)
    )
    decl += "("
    for p in func["parameters"]:
        decl += __get_type(p, templates) + " " + p["name"] + ", "
    decl = decl[:-2]
    decl += ")"
    return decl
