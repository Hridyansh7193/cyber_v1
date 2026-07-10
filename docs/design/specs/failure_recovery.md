# Failure Recovery Policy

BugHunter anticipates external binary crashes, timeouts, and logic errors. This policy strictly defines how different failure classes are handled.

## Recovery Strategies by Error Code

| Failure Class | Code Range | Trigger | Recovery Action |
| ------------- | ---------- | ------- | --------------- |
| **Missing Binary** | `P1001` | Tool not found on PATH. | **SKIP**. Plugin execution is bypassed safely. |
| **Unsupported Version** | `P1002` | Binary version mismatch. | **SKIP**. Mark plugin as UNVERIFIED. |
| **Timeout** | `E2001` | Tool exceeded Execution Budget. | **PARTIAL**. Save whatever raw stdout was generated, parse it, and continue. |
| **Parser Crash** | `R3001` | BugHunter parser throws an exception. | **PRESERVE**. Save raw stdout to evidence folder, log failure, and continue without finding generation. |
| **No Eligible Targets** | `E4001` | `is_candidate()` returned False for all. | **SKIP**. Bypass execution completely and log. |
| **Corrupted Report** | `R5001` | Report generator fails (I/O or serialization). | **ABORT REPORT**. Log error but preserve Database and Evidence untouched. |

Partial results are always preferable to losing everything. Silent data loss is unacceptable.
