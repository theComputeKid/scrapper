import os
import utils


def __get_link_macro(macro: str) -> str:
    return macro + "_EXPORT"


def __get_linkage_macro_header(macro: str) -> str:
    link_macro = __get_link_macro(macro)

    # Assign import/export macros for windows
    out = f"#ifdef _WIN32" + os.linesep
    out += f'#define {link_macro} extern "C" __declspec(dllexport)' + os.linesep

    # Assign import/export macros for unix
    out += f"#else" + os.linesep
    out += f'#define {link_macro} extern "C" __attribute__((visibility("default")))'
    out += os.linesep + f"#endif"
    return out


def __get_impl_cpp_signatures(config: dict) -> str:
    out = ""
    for f in config["functions"]:
        out += utils.get_function_signature_cpp(f, False) + ";" + os.linesep
    return out


def __get_impl_cpp_call(func: dict) -> str:
    out = f"\treturn {func['name']}("
    for p in func["parameters"]:
        out += p["name"] + ", "
    out = out[:-2] + ");"
    return out


def __get_impl_c_definitions(config: dict, mapping: dict[str, str]) -> str:
    out = ""
    for f in config["functions"]:
        type_combos = utils.get_template_combinations(f["templates"], f["combination"])
        for t in type_combos:
            out += __get_link_macro(config["linkage-macro"]) + " "
            out += utils.get_function_signature_c(f, t, mapping) + "{" + os.linesep
            out += __get_impl_cpp_call(f)
            out += os.linesep + "}" + os.linesep + os.linesep
        out += os.linesep
    return out


def get_impl(config: dict) -> str:
    suffixes = utils.get_type_suffix_list(config)
    out = utils.get_includes(config) + os.linesep + os.linesep
    out += __get_linkage_macro_header(config["linkage-macro"]) + os.linesep + os.linesep
    out += __get_impl_cpp_signatures(config) + os.linesep
    out += __get_impl_c_definitions(config, suffixes)
    return out
