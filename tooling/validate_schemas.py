"""Basic contract checks for schema repo."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "polymarket" / "trade" / "v1" / "schema.json"
VALID_EXAMPLE = (
    ROOT
    / "schemas"
    / "polymarket"
    / "trade"
    / "v1"
    / "examples"
    / "valid.json"
)
INVALID_EXAMPLE = (
    ROOT
    / "schemas"
    / "polymarket"
    / "trade"
    / "v1"
    / "examples"
    / "invalid-missing-field.json"
)


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _assert_required(data: dict, required: set[str]) -> None:
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"missing keys: {', '.join(sorted(missing))}")


def main() -> None:
    schema = _load_json(SCHEMA_PATH)
    valid = _load_json(VALID_EXAMPLE)
    invalid = _load_json(INVALID_EXAMPLE)

    _assert_required(schema, {"title", "type", "properties", "required"})
    _assert_required(valid, {"event_type", "event_version", "trade"})

    trade_required = set(
        schema["properties"]["trade"]["required"]
    )
    valid_trade = valid["trade"]
    invalid_trade = invalid["trade"]

    _assert_required(valid_trade, trade_required)

    missing_in_invalid = trade_required - set(invalid_trade.keys())
    if "transaction_hash" not in missing_in_invalid:
        raise ValueError(
            "invalid example is expected to miss transaction_hash"
        )

    print("schema checks passed")


if __name__ == "__main__":
    main()

