# Changelog
 
## [0.2.0] - 2026-04-28
 
### Added
- `polymarket.trade.v2.0.0` schema to support Polymarket CTF Exchange V2, which launched on April 28, 2026
- `condition_id` as a required field on the `trade` object — a bytes32 hex string identifying the Polymarket market the trade belongs to, now available directly from the transaction
### Changed
- `event_version` const updated to `2.0.0`
### Examples
- Added `valid.json` and `invalid-missing-field.json` for `v2.0.0`
- `invalid-missing-field.json` demonstrates a missing `condition_id`
---
 
## [0.1.0] - initial release

- Initialize schema platform repository
- Add `polymarket.trade.v1.0.0` schema and examples
- Add contract documentation and validation tooling

