import os
import utils


def __get_import_macro(macro: str) -> str:
    return macro + "_IMPORT"


def __get_linkage_macro_header(macro: str) -> str:
    extern_c_macro = macro + "_EXTERN_C"
    link_macro = __get_import_macro(macro)

    # ifdef C++
    out = f"#ifdef __cplusplus" + os.linesep
    out += f'#define {extern_c_macro} extern "C"' + os.linesep
    out += f"#else" + os.linesep
    out += f"#define {extern_c_macro}" + os.linesep
    out += f"#endif" + os.linesep + os.linesep

    # Assign import/export macros for windows
    out += f"#ifdef _WIN32" + os.linesep
    out += f"#define {link_macro} {extern_c_macro} __declspec(dllimport)" + os.linesep

    # Assign import/export macros for unix
    out += f"#else" + os.linesep
    out += f"#define {link_macro} {extern_c_macro}" + os.linesep
    out += f"#endif"
    return out


def __get_export_header_cpp_signatures(config: dict) -> str:
    out = f"#ifdef __cplusplus" + os.linesep
    for f in config["functions"]:
        out += utils.get_function_signature_cpp(f) + ";" + os.linesep
    out += f"#endif"
    return out


def __get_export_header_macros(config: dict) -> str:
    out = utils.get_includes(config) + os.linesep + os.linesep
    out += __get_linkage_macro_header(config["linkage-macro"])
    return out


def __get_export_header_c_signatures(config: dict) -> str:
    out = ""
    for f in config["functions"]:
        type_combos = utils.get_template_combinations(f["templates"], f["combination"])
        for t in type_combos:
            out += __get_import_macro(config["linkage-macro"]) + " "
            out += utils.get_function_signature_c(f, t, config["suffix-mapping"]) + ";"
            out += os.linesep
        out += os.linesep
    return out


def __get_export_header_cpp_definitions(config: dict) -> str:
    out = "// C++ wrapper impl." + os.linesep
    out += "#ifdef __cplusplus" + os.linesep
    out += "#include <type_traits>" + os.linesep + os.linesep
    for f in config["functions"]:
        out += (
            utils.get_export_header_cpp_definition(f, config["suffix-mapping"])
            + os.linesep
            + os.linesep
        )
    out += f"#endif"
    return out


def get_export_header(config: dict) -> str:
    out = __get_export_header_macros(config) + os.linesep + os.linesep
    out += __get_export_header_cpp_signatures(config) + os.linesep + os.linesep
    out += __get_export_header_c_signatures(config)
    out += __get_export_header_cpp_definitions(config)
    return out
