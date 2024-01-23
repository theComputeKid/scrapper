import os


def __get_type(arg: dict) -> str:
    t = arg["type"]
    if arg["const"]:
        t += " const"
    if arg["pointer"]:
        t += "*"
    return t


def __get_doxygen(func: dict) -> str:
    out = ""

    if "description" in func:
        out += "* @brief " + func["description"] + os.linesep

    for p in func["parameters"]:
        if "description" in p:
            out += f'* @param {p["name"]} {p["description"]}' + os.linesep

    if "description" in func["return"]:
        out += f'* @return {func["return"]["description"]}' + os.linesep

    if out:
        out = "/**" + os.linesep + out + "**/" + os.linesep
    return out


def get_function_signature_cpp(func: dict, doxygen=False) -> str:
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
    decl = ""
    if doxygen:
        decl += __get_doxygen(func)
    decl += "template <"
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
