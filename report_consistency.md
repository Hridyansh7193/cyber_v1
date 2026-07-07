# Report Consistency

This document validates the agreement between Telemetry, Workspace State, Database, and Reports.

## Consistency Audit Points

### 1. Telemetry vs Parsed Findings
- **Rule**: `stdout_size`, `parsed_objects`, and `success` must agree.
- **Status**: **PASS**. The `plugin_executor.py` logic now guarantees that `success = False` if `stdout_size > 0` and `parsed_findings == 0` without pre-existing errors. Telemetry generated directly aligns with the parser's extracted object size.

### 2. Workspace vs DiscoveredAssets
- **Rule**: All data mapped into `ExecutionState` must appear in the final report's `DiscoveredAssets` model.
- **Status**: **PASS**. Fields including `technologies`, `takeovers`, `fuzz_results`, and `secrets` are no longer dropped. They are explicitly pulled from `ExecutionState` during report generation inside `agents/reporter.py`.

### 3. Tool Versions in Telemetry and Reports
- **Rule**: The version of the tool invoked must be recorded accurately without defaulting to "unknown" unnecessarily.
- **Status**: **PASS**. `ToolManager.detect()` now proactively queries tools via `-version` or `--version` flags. The extracted string is populated directly into `ToolInfo`, ensuring that `reporter.py` can inject legitimate version telemetry into final generated reports.

### 4. Parameter and Fuzz Metadata Segregation
- **Rule**: Arjun discovering parameters and FFUF fuzzing must not overwrite or hijack each other's state domains.
- **Status**: **PASS**. Separated `NEW_PARAMETERS` for parameter discovery while correctly routing `NEW_FUZZ_RESULTS` back to `VulnerabilityState` for fuzzer logic.
