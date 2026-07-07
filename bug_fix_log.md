# Bug Fix Log

## Sprint: QA & Data Integrity Validation
**Role:** Senior Python Software Engineer & Release QA Engineer

### 1. Telemetry and Parser Drop Resolution
- **File:** `execution/plugin_executor.py`
- **Issue:** Parsed object length was measured via `len(parsed) if isinstance(parsed, list) else 0`, which counted characters for strings, and allowed tools throwing non-JSON to pass silently.
- **Fix:** Refactored into a `tuple()` builder and introduced a check: `if result.stdout_size > 0 and parsed_findings == 0`. Added an error payload causing `success=False`.

### 2. Discovered Assets Reconstruction
- **File:** `agents/reporter.py`
- **Issue:** Several populated vectors inside `ExecutionState` were abandoned during the translation into `DiscoveredAssets`.
- **Fix:** Directly mapped `secrets`, `technologies`, `takeovers`, and `fuzz_results` into the instantiated `DiscoveredAssets` model.

### 3. Orchestrator Missing Mapping Logic
- **File:** `orchestrator/wrapper_result_applier.py`
- **Issue:** Hardcoded tuple mappings inside `apply_vuln_wrapper_result` excluded FFUF fuzz outputs and Subzy takeover reports, leading to silent persistence loss.
- **Fix:** Implemented logic to capture `NEW_FUZZ_RESULTS` and `NEW_TAKEOVERS` and append them properly onto `new_vuln = VulnerabilityState(...)`. 

### 4. Added Missing State Fields
- **File:** `schemas/state.py`
- **Issue:** Found no storage mechanism for `fuzz_results` in any schema, meaning dropping was inevitable.
- **Fix:** Augmented `VulnerabilityState` to cleanly accommodate `fuzz_results`.

### 5. Tool Manager Dynamic Discovery
- **File:** `services/tool_manager.py`
- **Issue:** Version attributes defaulted to `None`, forcing reports to output `unknown` perpetually.
- **Fix:** Added `_detect_version` that aggressively runs `--version` / `-version` against identified binaries to capture semantic tags natively via Subprocess regex matches.

### 6. Meta Schema Collision Prevention
- **Files:** `execution/constants.py`, `execution/plugin_executor.py`, `execution/discovery/arjun_wrapper.py`, `orchestrator/wrapper_result_applier.py`
- **Issue:** To bypass schema validation, developers were hacking `arjun` parameter output through the `NEW_FUZZ_RESULTS` constant, causing conceptual overlap and logic bugs.
- **Fix:** Formalized `NEW_PARAMETERS`. Updated plugin executor validation logic, plugin output formats, and orchestrator parsing patterns.
