# ADR-002: Immutable Execution State Model

## Status
Accepted

## Context
As BugHunter pipelines grew, multiple components were mutating state indiscriminately, leading to unpredictable telemetry and race conditions during parallel execution.

## Alternatives Considered
- **Shared Mutable Dictionary**: Allowed global modifications from any wrapper. (Rejected: Impossible to track provenance or correlate findings accurately).
- **Database-Only State**: Query the SQLite DB for every pipeline step. (Rejected: Massive performance penalty during orchestration).

## Decision
We implemented an Immutable `ExecutionState` (Schema Version `2.0`), strictly owned by the `PluginExecutor` and `ScanService`. 
- **Owner**: `plugin_executor`
- **Modified by**: `wrapper_result_applier` (only when merging results after successful tool execution).
- **Read by**: `report_generator`, `persistence_service`.

## Consequences
- Data provenance is perfectly tracked.
- Pipeline state changes are strictly sequential and auditable.
- Finding generation becomes deterministic across identical inputs.
