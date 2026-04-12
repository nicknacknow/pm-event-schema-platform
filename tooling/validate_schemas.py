"""Basic contract checks for schema repo."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_ROOT = ROOT / "schemas"
SEMVER_FOLDER_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _assert_required(data: dict, required: set[str]) -> None:
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"missing keys: {', '.join(sorted(missing))}")


def _discover_schema_paths() -> list[Path]:
    schema_paths = sorted(SCHEMAS_ROOT.glob("**/v*.*.*/schema.json"))
    if not schema_paths:
        raise ValueError("no schema.json files found under schemas/**/v*.*.*/")
    return schema_paths


def _schema_coordinates(schema_path: Path) -> tuple[str, str, str]:
    relative_parts = schema_path.relative_to(SCHEMAS_ROOT).parts
    if len(relative_parts) != 4 or relative_parts[3] != "schema.json":
        raise ValueError(
            f"{schema_path}: expected schemas/<domain>/<event>/v<major>.<minor>.<patch>/schema.json"
        )

    domain, event, folder_version, _ = relative_parts
    if not SEMVER_FOLDER_RE.fullmatch(folder_version):
        raise ValueError(
            f"{schema_path}: version folder {folder_version!r} is not a semantic version "
            "in the form v<major>.<minor>.<patch>"
        )

    return domain, event, folder_version


def _assert_version_metadata(schema_path: Path, schema: dict) -> str:
    domain, event, folder_version = _schema_coordinates(schema_path)
    schema_version = folder_version[1:]
    properties = schema["properties"]
    _assert_required(properties, {"event_version", "trade"})
    _assert_required(properties["event_version"], {"const"})
    event_version = properties["event_version"]["const"]

    if event_version != schema_version:
        raise ValueError(
            f"{schema_path}: event_version const {event_version!r} "
            f"does not match folder version {schema_version!r}"
        )

    title = schema["title"]
    expected_title = f"{domain}.{event}.{folder_version}"
    if title != expected_title:
        raise ValueError(
            f"{schema_path}: schema title {title!r} does not match "
            f"expected title {expected_title!r}"
        )

    schema_id = schema["$id"]
    expected_schema_path = f"schemas/{domain}/{event}/{folder_version}/schema.json"
    if not schema_id.endswith(expected_schema_path):
        raise ValueError(
            f"{schema_path}: schema $id {schema_id!r} does not end with "
            f"expected schema path {expected_schema_path!r}"
        )

    return folder_version



def _validate_examples(schema_path: Path, schema: dict) -> None:
    examples_dir = schema_path.parent / "examples"
    valid_example = examples_dir / "valid.json"
    invalid_examples = sorted(examples_dir.glob("invalid*.json"))

    if not valid_example.exists():
        raise ValueError(f"{schema_path}: missing valid example at {valid_example}")
    if not invalid_examples:
        raise ValueError(f"{schema_path}: no invalid examples found in {examples_dir}")

    valid = _load_json(valid_example)

    _assert_required(valid, {"event_type", "event_version", "trade"})

    domain, event, folder_version = _schema_coordinates(schema_path)
    schema_version = folder_version[1:]
    if valid["event_type"] != event:
        raise ValueError(
            f"{valid_example}: event_type {valid['event_type']!r} does not match event folder {event!r}"
        )
    if valid["event_version"] != schema_version:
        raise ValueError(
            f"{valid_example}: event_version {valid['event_version']!r} "
            f"does not match folder version {schema_version!r}"
        )

    trade_required = set(schema["properties"]["trade"]["required"])
    valid_trade = valid["trade"]
    _assert_required(valid_trade, trade_required)

    for invalid_example in invalid_examples:
        invalid = _load_json(invalid_example)
        _assert_required(invalid, {"event_type", "event_version", "trade"})

        if invalid["event_type"] != event:
            raise ValueError(
                f"{invalid_example}: event_type {invalid['event_type']!r} does not match event folder {event!r}"
            )

        if invalid["event_version"] != schema_version:
            raise ValueError(
                f"{invalid_example}: event_version {invalid['event_version']!r} "
                f"does not match folder version {schema_version!r}"
            )

        invalid_trade = invalid["trade"]
        missing_in_invalid = trade_required - set(invalid_trade.keys())
        if not missing_in_invalid:
            raise ValueError(
                f"{invalid_example}: invalid example is expected to miss at "
                f"least one required trade field"
            )

        if (
            invalid_example.name == "invalid-missing-field.json"
            and "transaction_hash" not in missing_in_invalid
        ):
            raise ValueError(
                f"{invalid_example}: invalid example is expected to miss "
                "transaction_hash"
            )


def _validate_schema(schema_path: Path) -> None:
    schema = _load_json(schema_path)
    _assert_required(schema, {"$id", "title", "type", "properties", "required"})
    _assert_version_metadata(schema_path, schema)
    _validate_examples(schema_path, schema)


def main() -> None:
    schema_paths = _discover_schema_paths()
    for schema_path in schema_paths:
        _validate_schema(schema_path)

    print(f"schema checks passed for {len(schema_paths)} schema(s)")


if __name__ == "__main__":
    main()

