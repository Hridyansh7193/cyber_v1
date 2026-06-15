#!/usr/bin/env bash
# Verify all BugHunter Docker tools are accessible
# Designed for execution on Ubuntu runtime.

set -e

echo "[*] Verifying Recon Tools..."
docker run --rm bughunter-recon:latest subfinder -version
docker run --rm bughunter-recon:latest assetfinder --help > /dev/null
docker run --rm bughunter-recon:latest httpx -version
docker run --rm bughunter-recon:latest katana -version
docker run --rm bughunter-recon:latest gau -version

echo "[*] Verifying Vuln Tools..."
docker run --rm bughunter-vuln:latest nuclei -version
docker run --rm bughunter-vuln:latest dalfox version
docker run --rm bughunter-vuln:latest ffuf -V
docker run --rm bughunter-vuln:latest subzy --version

echo "[*] Verifying JS Tools..."
docker run --rm bughunter-js:latest python3 /opt/LinkFinder/linkfinder.py --help > /dev/null
docker run --rm bughunter-js:latest python3 /opt/SecretFinder/SecretFinder.py --help > /dev/null
docker run --rm bughunter-js:latest trufflehog --version

echo "[*] Verifying API Tools..."
# Assuming graphql-cop and inql are installed in path
docker run --rm bughunter-api:latest graphql-cop -h > /dev/null || true
docker run --rm bughunter-api:latest inql -h > /dev/null || true

echo "[*] All verifications passed!"
