# Report Invariants

The following invariants MUST hold true for any generated report:

1. `report.target != session_id`
   - The target must be the domain or IP, not the UUID session identifier.
2. `report.target == canonical scan target`
   - Must match `state.target.domain`.
3. `end_time >= start_time` when both exist.
4. `duration_seconds >= 0` when measured.
5. `missing duration != fabricated zero`
   - If duration is not measured, it must not be rendered as 0s.
6. `report.finding_count == len(report.findings)`
7. `sum(severity_counts.values()) == report.finding_count`
8. `report.error_count == canonical finalized error count`
   - Must equal the total errors present in `state.logs`.
9. `CLI error count == report error count` for the same finalized scan.
10. Plugin summary status derives from canonical execution status (`state.logs`).
11. Timeline ordering is deterministic (chronological by start time, tie-breaker on plugin name).
12. Finding ordering is deterministic (by severity, then id).
13. The same finalized scan state produces semantically identical report content except explicitly allowed volatile fields (like generation timestamp).
14. `NOT_MEASURED != MEASURED_ZERO`
    - A plugin that did not run (NOT_MEASURED) must not be reported as finding 0 assets.
15. Accepted findings must satisfy `Finding` quality requirements (e.g. no missing mandatory fields).
16. Parser-invalid records must remain observable (captured in errors).
