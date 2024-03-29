import os
import utils


def __get_import_macro(macro: str) -> str:
    return macro + "_IMPORT"


def __get_linkage_macro_header(macro: str) -> str:
    extern_c_macro = macro + "_EXTERN_C"
    link_macro = __get_import_macro(macro)

    out = f"#ifndef {link_macro}" + os.linesep

    # ifdef C++
    out += f"#\tifdef __cplusplus" + os.linesep
    out += f'#\t\tdefine {extern_c_macro} extern "C"' + os.linesep
    out += f"#\telse" + os.linesep
    out += f"#\t\tdefine {extern_c_macro}" + os.linesep
    out += f"#\tendif" + os.linesep + os.linesep

    # Assign import/export macros for windows
    out += f"#\tifdef _WIN32" + os.linesep
    out += (
        f"#\t\tdefine {link_macro} {extern_c_macro} __declspec(dllimport)" + os.linesep
    )

    # Assign import/export macros for unix
    out += f"#\telse" + os.linesep
    out += f"#\t\tdefine {link_macro} {extern_c_macro}" + os.linesep
    out += f"#\tendif" + os.linesep
    out += f"#endif"
    return out


def __get_export_header_cpp_signatures(config: dict) -> str:
    out = ""
    for f in config["functions"]:
        out += utils.get_function_signature_cpp(f, True) + ";" + os.linesep
    return out


def __get_export_header_macros(config: dict) -> str:
    out = utils.get_includes(config) + os.linesep
    macro = utils.get_macro(config)
    out += __get_linkage_macro_header(macro)
    return out


def __get_export_header_c_signatures(config: dict) -> str:
    out = ""
    macro = utils.get_macro(config)
    for f in config["functions"]:
        type_combos = utils.get_template_combinations(f["templates"], f["combination"])
        for t in type_combos:
            out += __get_import_macro(macro) + " "
            out += utils.get_function_signature_c(f, t, config["mapping"]) + ";"
            out += os.linesep
        out += os.linesep
    return out


def __get_export_header_cpp_definitions(config: dict) -> str:
    out = "#include <type_traits>" + os.linesep + os.linesep
    for f in config["functions"]:
        out += (
            utils.get_export_header_cpp_definition(f, config["mapping"])
            + os.linesep
            + os.linesep
        )
    return out


def get_export_header(config: dict) -> tuple[str, str, str, str]:
    macros = __get_export_header_macros(config) + os.linesep
    cpp_sig = __get_export_header_cpp_signatures(config)
    c_sig = __get_export_header_c_signatures(config)
    cpp_def = __get_export_header_cpp_definitions(config)
    return macros, c_sig, cpp_sig, cpp_def
