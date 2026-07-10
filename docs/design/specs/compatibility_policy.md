# Compatibility Policy

This document defines the stability guarantees and release contracts for BugHunter interfaces.

## v1.x Guarantees
During the `v1.x` lifecycle, the following are strictly **frozen**:
- **Plugin API (`PLUGIN_INTERFACE_VERSION = "1.0"`)**: No breaking changes. New capabilities must be optional or additive with fallback defaults.
- **Report Schema (`REPORT_SCHEMA_VERSION = "1.0"`)**: No removal or renaming of JSON keys. Only additive fields.
- **Database Schema**: No dropping columns or tables without backward-compatible views.
- **CLI UX**: Commands like `bughunter scan`, `resume`, `report`, and `doctor` will not change their positional arguments or core flags.
- **Workspace Layout**: The internal directory structure of `workspace/` remains stable.

## v2.0+ Rules
Breaking changes are reserved exclusively for major version increments (`v2.x`). When updating a schema to v2:
- A migration guide must be published.
- Internal adapters must be provided where feasible to ease transitions.
