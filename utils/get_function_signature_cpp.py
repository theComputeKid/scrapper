def __get_type(arg: dict) -> str:
    t = arg["type"]
    if arg["const"]:
        t += " const"
    if arg["pointer"]:
        t += "*"
    return t


def get_function_signature_cpp(func: dict) -> str:
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
    decl = "template <"
    for template in func["templates"]:
        decl += f'typename {template["name"]}'
        decl += ", "
    decl = decl[:-2] + "> "

    decl += __get_type(func["return"]) + " "
    decl += func["name"]
    decl += "("
    for p in func["parameters"]:
        decl += __get_type(p) + " " + p["name"] + ", "
    decl = decl[:-2]
    decl += ")"

    return decl
