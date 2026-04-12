# pm-event-schema-platform

Central source of truth for event schemas, examples, and contract rules.

This repository is language-agnostic. Service repos (publishers/listeners) should use these schema contracts and implement local serializers/deserializers or generated bindings.

## Structure

```text
schemas/      # versioned JSON schemas by domain
contracts/    # naming, topic, and versioning rules
examples/     # canonical payload examples (inside each schema version folder)
tooling/      # local validation scripts
ci/           # CI workflows for schema checks
```

## Current event contract

- `schemas/polymarket/trade/v1.0.0/schema.json`
  - semantic version path format: `v<major>.<minor>.<patch>`
- examples:
  - `schemas/polymarket/trade/v1.0.0/examples/valid.json`
  - `schemas/polymarket/trade/v1.0.0/examples/invalid-missing-field.json`

## Usage model

1. Publisher emits payloads that conform to the schema.
2. Listener validates/deserializes against the same schema contract.
3. Breaking changes create a new version folder (for example `v2.0.0`) without mutating prior versions.

## Considerations

1. Consider when creating a new schema whether some fields should be under a 'common' folder, if they are used elsewhere. 

