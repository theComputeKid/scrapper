#!/usr/bin/env python3
import argparse, pathlib, json
import utils


def get_impl(input_json: pathlib.Path) -> str:
    config = json.loads(input_json.read_text())
    return utils.get_impl(config)


def get_export_header(input_json: pathlib.Path) -> str:
    config = json.loads(input_json.read_text())
    return utils.get_export_header(config)


def exec(
    input_json: pathlib.Path,
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
    output_header_file.write_bytes(output_header_file_text.encode())

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
    exec(input_json, output_header_file, output_impl_file)
