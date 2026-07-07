# Parser Validation

This document validates parser integrity, inputs, outputs, errors, and records.

## 1. Input Integrity
- All plugins inherit from `BaseExecutionPlugin` or implement `ExecutionPlugin`.
- Standard inputs: `stdout` and `stderr` are safely passed as strings.
- Out-of-band records: The `plugin_executor` guarantees raw logs are captured on disk in `/workspaces/domain/sessions/id/evidence/plugin_stdout.log` regardless of whether parsing succeeds.

## 2. Output and Error Handling Correctness
| Plugin | Output Type | Error Handling | Status |
|--------|-------------|----------------|--------|
| httpx | JSON-lines | Silent drops on error | PASS |
| nuclei | JSON-lines | Silent drops on error | PASS |
| dalfox | JSON-lines | Silent drops on error | PASS |
| ffuf | JSON-lines | Silent drops on error | PASS |
| arjun | Regex (Text) | Regex matching | PASS (Parameters now mapped correctly) |
| katana | JSON-lines | Silent drops on error | PASS |
| subfinder| String-lines| Skip blank lines | PASS |

## 3. Discrepancy Mitigations
- **Silent Validation Fallback**: By appending `errors.append("Stdout was not empty but 0 objects were parsed.")` in `plugin_executor.py`, BugHunter is now strictly capable of rejecting parsers that fail to parse output rather than assuming the scan yielded zero results successfully.
- **Tuple Mappings**: Fixes applied in `plugin_executor.py` ensure `parsed_findings` accurately measures the object count instead of string character count by applying a robust tuple coercion logic.
