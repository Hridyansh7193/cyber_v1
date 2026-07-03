# BugHunter CLI Validation Report

Date: 2026-07-03

Summary: Executed core CLI commands and captured outputs. Raw logs are in `validation_outputs/cli/` and command-level outputs in `validation_outputs/`.

## Commands executed and outcomes

- `bughunter --version`
  - Output: `BugHunter v0.1.0`
  - Evidence: `validation_outputs/pip_editable.log` (install) and general command run during setup

- `bughunter doctor`
  - Exit code: 0
  - stdout captured: `validation_outputs/doctor_stdout2.txt` (contains "BugHunter Doctor" summary)
  - stderr captured: `validation_outputs/doctor_stderr2.txt` (empty after `psutil` fix)
  - Key lines: "Summary: 21 Passed, 1 Warnings, 0 Failed"

- `bughunter verify`
  - Exit code: 0
  - stdout captured: `validation_outputs/verify_stdout.txt`
  - stderr captured: `validation_outputs/verify_stderr.txt` (empty)
  - Key behavior: Performed a verification scan against `scanme.nmap.org` and executed multiple plugins (subfinder, httpx, assetfinder, gau, linkfinder). Some plugins returned non-zero exits (httpx had Exit code: 2 on first try but retried).

- Other CLI commands (help, plugins, jobs, workspace list, search test, report --help, scan --help, planner --help, logs --help, telemetry --help)
  - Captured outputs saved under `validation_outputs/cli/` as individual stdout/stderr files for later inspection. Some command runs were long-running and are saved in those files.

## Observations

- CLI startup and core commands run without import errors after installing missing dependency `psutil`.
- `bughunter verify` executed an actual verification scan using installed binaries and returned successful exit codes for the overall run; plugin-level exits varied and are recorded in `validation_outputs/verify_stdout.txt`.

## Evidence files

- [validation_outputs/doctor_stdout2.txt](validation_outputs/doctor_stdout2.txt)
- [validation_outputs/doctor_stderr2.txt](validation_outputs/doctor_stderr2.txt)
- [validation_outputs/verify_stdout.txt](validation_outputs/verify_stdout.txt)
- [validation_outputs/verify_stderr.txt](validation_outputs/verify_stderr.txt)
- `validation_outputs/tools_check.txt`
- `validation_outputs/cli/` (individual CLI command stdout/stderr files)

