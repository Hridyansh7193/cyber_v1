# Data Flow Audit

## 1. Raw Output → Parsed Output
- **Raw Execution**: `ProcessRunner` executes tools and captures `stdout` and `stderr` as strings, ensuring no terminal escape sequences break parsing (for standard plugins).
- **Parsing**: `PluginExecutor` invokes each plugin's `parse(stdout, stderr)` method.
- **Issue Discovered**: Tools outputting usage/banner info on `stdout` without any parsers matching could result in `len(parsed) == 0`. The system recorded this as a "silent success".
- **Resolution**: `PluginExecutor` now correctly records an error if `stdout_size > 0` but `parsed_findings == 0`, ensuring `success=False` for silent failures. Also fixed `tuple()` generation logic where string outputs were incorrectly counted as individual characters instead of single elements.

## 2. Parsed Output → ToolResult
- The `parsed` objects are mapped to `ToolResult.parsed_output` as a strictly-typed `tuple`.
- Plugins convert `parsed` output into generic taxonomy structures by overriding `build_metadata(parsed)`.
- **Issue Discovered**: Tools discovering new parameters (e.g. `arjun`) hijacked `new_fuzz_results` to bypass `PluginExecutor` metadata validation schema rules, because `new_parameters` wasn't whitelisted.
- **Resolution**: Created `NEW_PARAMETERS` constant and added `new_parameters` to `valid_keys` in `PluginExecutor`. Updated `arjun` to return `NEW_PARAMETERS`.

## 3. ToolResult → ExecutionState
- The orchestrator maps `ToolResult` into `ExecutionState` via `wrapper_result_applier.py`.
- **Issue Discovered**: `apply_vuln_wrapper_result` silently dropped `ffuf` (`NEW_FUZZ_RESULTS`) and `subzy` (`NEW_TAKEOVERS`) metadata.
- **Resolution**: `VulnerabilityState` schema was updated to store `fuzz_results`. `wrapper_result_applier.py` was updated to explicitly extract `NEW_FUZZ_RESULTS` and `NEW_TAKEOVERS` and inject them into the returned state.

## 4. ExecutionState → Report
- `agents/reporter.py` consolidates `ExecutionState` into a standalone `Report` object.
- **Issue Discovered**: Missing field mappings in `DiscoveredAssets` (e.g., `technologies`, `takeovers`, `fuzz_results`, `secrets`).
- **Resolution**: `DiscoveredAssets` object instantiation was updated to map missing state attributes properly.

## 5. Persistence
- Snapshots are checkpointed accurately by `OrchestratorAdapter` reading `ExecutionState`.
- Report data is guaranteed pure by relying exclusively on `ExecutionState` and extracting consistent telemetry records.

**Conclusion**: The state transition mapping is now 1:1, ensuring no discovered assets are lost between the parser and the final JSON/Markdown report.
