# BugHunter Release Engineering

## Branching Strategy

- `main`: Stable releases only. Code on `main` is always production-ready.
- `develop`: Integration branch. All features merge here first.
- `feature/*`: One feature per branch.
- `release/*`: Release stabilization (e.g., `release/v1.0.0-rc1`).
- `hotfix/*`: Emergency fixes branching directly from `main`.

## Semantic Versioning (SemVer)

BugHunter follows Semantic Versioning (`MAJOR.MINOR.PATCH`).
This applies to the CLI, Plugin Interface, Report Schema, and Database Schema.

- **MAJOR (v1.0.0 -> v2.0.0)**: Breaking API changes. Schemas may change destructively.
- **MINOR (v1.0.0 -> v1.1.0)**: New backwards-compatible features (e.g., adding a new plugin, adding additive fields to the database).
- **PATCH (v1.0.0 -> v1.0.1)**: Bug fixes only. No schema changes.

## Supported External Dependencies

BugHunter freezes support for the following tool versions to guarantee deterministic outcomes:

| Tool | Supported Version |
|---|---|
| Python | 3.12 |
| Nuclei | 3.x |
| Subfinder | 2.x |
| Katana | 1.x |
| Dalfox | 2.x |
| Ffuf | 2.x |
