#!/usr/bin/env python3
import argparse, pathlib, json, os
import utils


def __write_if_needed(text: str, output: pathlib.Path) -> None:
    new = text.encode()
    if output.is_file():
        old = output.read_bytes()
        if old != new:
            print(f"Updating file: {output}")
            output.write_bytes(new)
    else:
        print(f"Writing file: {output}")
        output.write_bytes(new)


def __write_split_header(header: list[str], output_header_file: pathlib.Path) -> None:
    # * Write C++ wrapper file.
    cpp_def_file = output_header_file.stem + "Impl.hpp"
    cpp_def_file_path = output_header_file.parent / cpp_def_file

    cpp_def_text = (
        "/** @file */"
        + os.linesep
        + "#pragma once"
        + os.linesep
        + f'#include "{output_header_file.name}"'
        + os.linesep
        + header[3]
    )
    __write_if_needed(cpp_def_text, cpp_def_file_path)

    # * Write main header file.
    out = (
        "/** @file */"
        + os.linesep
        + "#pragma once"
        + os.linesep
        + header[0]
        + os.linesep
        + header[1]
        + "#ifdef __cplusplus"
        + os.linesep
        + header[2]
        + f'#include "{cpp_def_file}"'
        + os.linesep
        + "#endif"
    )
    __write_if_needed(out, output_header_file)


def __write_combined_header(header: list[str], output_file: pathlib.Path) -> None:
    out = (
        "/** @file */"
        + os.linesep
        + f"#pragma once"
        + os.linesep
        + header[0]
        + os.linesep
        + header[1]
        + "#ifdef __cplusplus"
        + os.linesep
        + header[2]
        + os.linesep
        + header[3]
        + "#endif"
    )
    __write_if_needed(out, output_file)


def __extract_JSON(input_json: pathlib.Path) -> dict:
    config = json.loads(input_json.read_text())
    utils.validate_schema(config)
    suffixes = utils.get_type_suffix_list(config)
    config["mapping"] = suffixes

    for f in config["functions"]:
        if not "combination" in f:
            f["combination"] = "all"

    return config


def get_impl(input_json: pathlib.Path) -> str:
    config = __extract_JSON(input_json)
    return utils.get_impl(config)


def get_export_header(input_json: pathlib.Path) -> str:
    config = __extract_JSON(input_json)
    return utils.get_export_header(config)


def exec(
    input_json: pathlib.Path,
    separate_header: bool,
    output_header_file: pathlib.Path,
    output_impl_file: pathlib.Path,
) -> None:
    """Generates C and C++ wrappers from a JSON config file.

    Parameters
    ----------
    input_json : pathlib.Path
        Path to the JSON config file containing the function configurations.

    output_header_file : pathlib.Path
        Path wherethe generated output header file will be saved.

    Raises
    ------
    ValidationError
        If the JSON config does not obey the package schema.
    """
    output_header_file_text = get_export_header(input_json)
    output_header_file.parent.mkdir(parents=True, exist_ok=True)

    if separate_header:
        __write_split_header(output_header_file_text, output_header_file)
    else:
        __write_combined_header(output_header_file_text, output_header_file)

    implementation_file_text = get_impl(input_json)
    output_impl_file.parent.mkdir(parents=True, exist_ok=True)
    output_impl_file.write_bytes(implementation_file_text.encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="scrapper",
        description="A script to generate c convenience wrappers for c++.",
    )
    parser.add_argument(
        "input",
        nargs=1,
        help="Path to the input JSON file that describes the C++ function to generate C functions for.",
    )
    parser.add_argument(
        "-oh",
        "--output-header",
        nargs=1,
        required=True,
        help="Path to the output header file.",
    )
    parser.add_argument(
        "-s",
        "--separate-header",
        action="store_true",
        help="Seperate the exported header into its interface and implementation",
    )
    parser.add_argument(
        "-oi",
        "--output-impl",
        nargs=1,
        required=True,
        help="Path to the output implementation file.",
    )
    args = parser.parse_args()
    input_json = pathlib.Path(args.input[0]).resolve()
    output_header_file = pathlib.Path(args.output_header[0]).resolve()
    output_impl_file = pathlib.Path(args.output_impl[0]).resolve()
    exec(input_json, args.separate_header, output_header_file, output_impl_file)
