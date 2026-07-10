# ADR-004: Evidence-Driven Reporting

## Status
Accepted

## Context
Original reports relied solely on the parsed structural output of the plugins. If a parser had a bug, the finding was lost or corrupted, with no raw data available to verify or debug the result.

## Alternatives Considered
- **Store Full Stdout in Database**: (Rejected: SQLite databases bloat significantly when storing megabytes of raw stdout logs).
- **Transient Evidence**: Storing evidence temporarily during execution and discarding it after the report is built. (Rejected: Prevents historical analysis and replayability).

## Decision
We implement a strict Evidence Storage requirement for the `workspace` directory. Every finding must be traceable down an evidence chain:
`tool -> command -> request -> response -> stdout -> stderr -> parsed -> finding -> report`

## Consequences
- Every finding is reproducible.
- Replaying requests via `curl` or Burp becomes trivial.
- False-negative analysis becomes possible by inspecting the raw evidence against the expected ground truth.
