# BugHunter Tool Verification Report

Date: 2026-07-03

Summary: Probe of external tools required by BugHunter. Results saved in `validation_outputs/tools_check.txt`.

## Results (high level)

- Present and version-detected:
  - `subfinder` — /home/akshat/go/bin/subfinder — v2.14.0
  - `katana` — /home/akshat/go/bin/katana — v1.6.1
  - `gau` — /home/akshat/go/bin/gau — v2.2.4
  - `dnsx` — /home/akshat/go/bin/dnsx — v1.2.3
  - `naabu` — /home/akshat/go/bin/naabu — v2.6.1
  - `nuclei` — /home/akshat/go/bin/nuclei — v3.10.0
  - `dalfox` — /home/akshat/go/bin/dalfox — version available via `dalfox version` command
  - `ffuf` — /home/akshat/go/bin/ffuf — v2.1.0-dev
  - `assetfinder` — /home/akshat/go/bin/assetfinder — present (no `--version` flag)
  - `waybackurls` — /home/akshat/go/bin/waybackurls — present (no `--version` flag)
  - `httpx` — /home/akshat/Desktop/project/cyber_v1/.venv/bin/httpx — present (no `--version` flag)
  - `linkfinder` — not present in PATH (not detected)
  - `secretfinder` — not present in PATH (not detected)
  - `subzy` — not present in PATH (not detected)
  - `trufflehog` — not present in PATH (not detected)

## Notes and issues

- Several tools (assetfinder, waybackurls, assetfinder) do not support the `--version` flag; their usage/help output printed instead.
- `httpx` in the Python virtualenv is the Python HTTPX package CLI and does not expose a `--version` flag; its presence was detected but behavior differs from expected Golang `httpx` binary.
- `linkfinder`, `secretfinder`, `subzy`, and `trufflehog` were not found in PATH. These are required for full validation.
- `docker` is not installed; some parts of the system may expect Docker for containerized tools.

## Evidence

See `validation_outputs/tools_check.txt` for the full captured output and exact command responses.

## Recommended next steps

- Install missing tools: `linkfinder`, `secretfinder`, `subzy`, and `trufflehog` via their project installation instructions.
- Consider installing Docker if required by user workflows or to run certain tools in containers.
- For tools without `--version` flags, adjust the verification script to run their explicit `version` subcommand if supported (e.g., `dalfox version`).

