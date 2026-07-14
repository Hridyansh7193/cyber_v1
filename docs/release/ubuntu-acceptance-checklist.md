# Ubuntu 24.04 Acceptance Checklist

Before officially stamping BugHunter v1.0, the following manual acceptance tests MUST be performed on a clean Ubuntu 24.04 LTS instance. This ensures that the agent works seamlessly in its canonical environment.

## 1. Environment Setup

- [ ] Verify Ubuntu 24.04 LTS is active (`cat /etc/os-release`).
- [ ] Install dependencies: `sudo apt update && sudo apt install python3 python3-venv python3-pip golang-go git curl`.
- [ ] Create and activate Python virtual environment: `python3 -m venv venv && source venv/bin/activate`.
- [ ] Install BugHunter: `pip install -e .`.

## 2. Dependency Installation

- [ ] Run BugHunter doctor: `bughunter doctor`. Observe missing tool warnings.
- [ ] Run BugHunter installer: `bughunter install`.
- [ ] Ensure binaries (like `subfinder`, `nuclei`, `httpx`) are installed into `~/go/bin`.
- [ ] Run `bughunter doctor` again. It should now report all external tools as available and correctly resolved (preventing `httpx` module collision).

## 3. Basic Execution (Recon)

- [ ] Execute a basic scan: `bughunter scan juice-shop.herokuapp.com --profile fast`.
- [ ] Verify `subfinder` process correctly executes and writes subdomains to the console.
- [ ] Verify execution telemetry and logs correctly capture process output inside the workspace directory (`workspaces/juice-shop_herokuapp_com_<hash>/sessions/...`).

## 4. Full Execution (Docker Juice Shop)

- [ ] Start an OWASP Juice Shop instance via Docker: `docker run --rm -p 3000:3000 bkimminich/juice-shop`.
- [ ] Execute a full scan against the local target: `bughunter scan localhost:3000 --profile default`.
- [ ] Validate workspace path sanitization: Ensure the workspace directory is named `localhost_3000_<hash>` and not attempting path traversal or failing due to the colon.
- [ ] Wait for execution to complete. Verify findings are generated.

## 5. Teardown & Reporting

- [ ] Run the report generator for the completed session: `bughunter report <session-id> --format markdown`.
- [ ] Ensure the Markdown file is generated without path traversal vulnerabilities.
- [ ] Run `bughunter workspace clean` and verify temporary files are purged.
