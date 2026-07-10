# BugHunter Project Philosophy

BugHunter was designed with a strict set of architectural boundaries. When contributing or reviewing PRs, these philosophical principles must always be upheld.

## 1. Correctness Over Speed
BugHunter prefers to execute slowly and accurately rather than fast and erroneously. Rate limiting, timeouts, and resource budgets exist to prevent the orchestration engine from overwhelming both the target and the host machine.

## 2. Every Finding Must Be Reproducible
If BugHunter reports a vulnerability or finding, there must be a traceable chain of raw evidence to support it. 

## 3. Every Parser Failure Must Be Observable
If an external tool crashes or produces unexpected JSON, BugHunter must never silently drop the data. It must log the failure (`R3001 PARSER_FAILURE`) and preserve the raw stdout for analysis.

## 4. No Silent Data Loss
Partial results are always preferable to losing everything. If a plugin runs for 4 hours and then times out, the parser must recover whatever JSON lines were emitted prior to the crash.

## 5. Plugins Are Isolated
Plugins (`ExecutionPlugin`) do not communicate with each other directly. They strictly read from `ExecutionState` and return parsed outputs. The orchestrator is solely responsible for merging results.

## 6. Reports Never Invent Information
Reports must be deterministic reflections of the database. BugHunter will never use LLMs or heuristic generation to hallucinate severity scores or vulnerability claims that were not explicitly proven by the underlying tools.
