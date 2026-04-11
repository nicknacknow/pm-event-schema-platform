# Versioning policy

1. Existing versions are immutable once released.
2. Non-breaking additions may update the same major version only if all consumers tolerate them.
3. Breaking changes require a new version folder (for example `v2`).
4. Producers should emit exactly one contract version per topic unless migration is active.
5. During migration, dual-publish to separate topics or include explicit version routing.

