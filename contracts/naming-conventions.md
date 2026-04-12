# Naming conventions

- Schema path format: `schemas/<domain>/<event>/<version>/schema.json`
- Version folders use semantic versions: `v1.0.0`, `v1.1.0`, `v2.0.0`, ...
- Event schema title format: `<domain>.<event>.v<major>.<minor>.<patch>`
- Topic names use lowercase dotted names, e.g. `trades.raw`, `alerts.large-wallet`

