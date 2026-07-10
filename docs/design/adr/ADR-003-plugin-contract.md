# ADR-003: Plugin Contract Versioning

## Status
Accepted

## Context
Plugins encapsulate logic for executing external bug hunting binaries. As we introduce new orchestration features (chunking, partial results, dependencies), the `BaseExecutionPlugin` interface evolves, threatening to break backward compatibility.

## Alternatives Considered
- **Implicit Contracts**: Relying on duck-typing and `hasattr` checks in the executor. (Rejected: Brittle and hard to maintain).
- **SemVer on Plugins Only**: Versioning the individual plugins, but not the interface they implement. (Rejected: Does not guarantee that a plugin correctly implements the pipeline's expected interface).

## Decision
We enforce a strict `PLUGIN_INTERFACE_VERSION` in `schemas/versions.py`. Every plugin must adhere to `Plugin Interface v1`. Breaking changes to the plugin contract will require incrementing to `v2` and providing a migration path.

## Consequences
- The orchestrator can trust that all validated plugins adhere strictly to the `v1` contract.
- Extending plugin capabilities (e.g., adding `supports_partial_results`) requires careful schema version management.
