#!/bin/bash
set -Eeuo pipefail

echo "BugHunter V1 Final Acceptance Test"
echo "=================================="

# Check git status
if ! git diff --exit-code > /dev/null 2>&1; then
    echo "ERROR: Git working directory is not clean. Commit changes first."
    exit 1
fi

echo "[1/7] Creating fresh virtual environments..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip build wheel

echo "[2/7] Running editable install test..."
pip install -e .
bughunter --help > /dev/null
bughunter --version
bughunter doctor > /dev/null

echo "[3/7] Building wheel..."
python -m build --wheel
WHEEL_FILE=$(ls dist/bughunter-1.0.0-*.whl)

echo "[4/7] Running check_package.py..."
python scripts/check_package.py

echo "[5/7] Creating isolated test environment..."
deactivate
python3 -m venv testenv
source testenv/bin/activate
pip install --upgrade pip

echo "[6/7] Testing wheel installation..."
pip install "$WHEEL_FILE"
echo "Testing bughunter execution from wheel..."
which bughunter
bughunter --help > /dev/null
bughunter doctor > /dev/null
bughunter install --dry-run
bughunter verify
bughunter self-test
bughunter plugins > /dev/null

echo "[7/7] Generating release.json metadata..."
cat <<EOF > release.json
{
  "version": "1.0.0",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "build_date": "$(date -Iseconds)",
  "python": "$(python --version 2>&1)",
  "schema": "v2",
  "plugins": "14",
  "profile_version": "v1",
  "config_version": "v2"
}
EOF

echo "=================================="
echo "SUCCESS: V1 Acceptance Complete."
