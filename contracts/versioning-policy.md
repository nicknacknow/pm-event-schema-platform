# Versioning policy

1. Existing versions are immutable once released.
2. Schema versions use semantic versioning: `major.minor.patch` (for example `1.0.0`).
3. Non-breaking additions/changes increment minor or patch versions (`1.1.0`, `1.1.1`).
4. Breaking changes require a new major version (`2.0.0`).
5. Producers should emit exactly one contract version per topic unless migration is active.
6. During migration, dual-publish to separate topics or include explicit version routing.

