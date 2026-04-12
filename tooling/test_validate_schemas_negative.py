"""Regression checks for invalid schema fixtures."""

from __future__ import annotations

from pathlib import Path

import validate_schemas

FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures" / "validator"


def _run_expected_failure(case_name: str, expected_message: str) -> None:
    fixture_root = FIXTURES_ROOT / case_name
    original_root = validate_schemas.ROOT
    original_schemas_root = validate_schemas.SCHEMAS_ROOT

    try:
        validate_schemas.ROOT = fixture_root
        validate_schemas.SCHEMAS_ROOT = fixture_root / "schemas"

        schema_paths = validate_schemas._discover_schema_paths()
        if len(schema_paths) != 1:
            raise AssertionError(
                f"{case_name}: expected exactly one schema path, found {len(schema_paths)}"
            )

        try:
            validate_schemas._validate_schema(schema_paths[0])
        except ValueError as exc:
            message = str(exc)
            if expected_message not in message:
                raise AssertionError(
                    f"{case_name}: expected error containing {expected_message!r}, got {message!r}"
                ) from exc
        else:
            raise AssertionError(f"{case_name}: expected validator failure")
    finally:
        validate_schemas.ROOT = original_root
        validate_schemas.SCHEMAS_ROOT = original_schemas_root


def main() -> None:
    _run_expected_failure("bad-version-folder", "semantic version")
    _run_expected_failure("mismatched-title", "expected title")
    print("negative schema fixtures failed as expected")


if __name__ == "__main__":
    main()