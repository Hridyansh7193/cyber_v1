# ADR-005: Chunk-Level Execution Resume

## Status
Accepted

## Context
Large scans can fail or time out after executing 90% of their targets. Restarting the entire plugin from scratch wastes hours and burns execution budgets.

## Alternatives Considered
- **Node-level Resume**: Simply skipping plugins that successfully finished, but restarting plugins that failed midway. (Rejected: Insufficient granularity for tools that take hours to run).
- **Line-by-line Resume**: Resuming exactly from the last processed target. (Rejected: High I/O overhead and complex to manage for non-linear tools).

## Decision
We implement **Chunk-level Resume**. Targets provided to plugins are chunked, and state is preserved per-chunk. If a plugin fails, the resume mechanism will restart execution specifically from the failed chunk index.

## Consequences
- Massive runtime savings when recovering from network drops or timeouts.
- Execution tracking logic becomes slightly more complex, requiring chunk offsets in the execution state database.
