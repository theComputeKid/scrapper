import pathlib, json, jsonschema


def __get_schema_path() -> pathlib.Path:
    """Get the absolute path to the JSON schema used for validation."""
    my_current_directory = pathlib.Path(__file__).parents[1].resolve()
    schema = my_current_directory / "utils" / "schema.json"
    return schema


def validate_schema(config: dict):
    schema = json.loads(__get_schema_path().read_text())
    jsonschema.validate(config, schema=schema)
