"""Basic contract checks for schema repo."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_ROOT = ROOT / "schemas"


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


def _assert_version_metadata(schema_path: Path, schema: dict) -> str:
    folder_version = schema_path.parent.name
    properties = schema["properties"]
    event_version = properties["event_version"]["const"]

    if event_version != folder_version:
        raise ValueError(
            f"{schema_path}: event_version const {event_version!r} "
            f"does not match folder version {folder_version!r}"
        )

    title = schema["title"]
    if folder_version not in title:
        raise ValueError(
            f"{schema_path}: schema title {title!r} does not include "
            f"folder version {folder_version!r}"
        )

    schema_id = schema["$id"]
    if folder_version not in schema_id:
        raise ValueError(
            f"{schema_path}: schema $id {schema_id!r} does not include "
            f"folder version {folder_version!r}"
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

    folder_version = schema_path.parent.name
    if valid["event_version"] != folder_version:
        raise ValueError(
            f"{valid_example}: event_version {valid['event_version']!r} "
            f"does not match folder version {folder_version!r}"
        )

    trade_required = set(schema["properties"]["trade"]["required"])
    valid_trade = valid["trade"]
    _assert_required(valid_trade, trade_required)

    for invalid_example in invalid_examples:
        invalid = _load_json(invalid_example)
        _assert_required(invalid, {"event_type", "event_version", "trade"})

        if invalid["event_version"] != folder_version:
            raise ValueError(
                f"{invalid_example}: event_version {invalid['event_version']!r} "
                f"does not match folder version {folder_version!r}"
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

