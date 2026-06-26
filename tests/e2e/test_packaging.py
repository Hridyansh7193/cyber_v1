import pytest
import subprocess
from pathlib import Path
from version import __version__

def test_bughunter_executable_exists():
    import shutil
    assert shutil.which("bughunter") is not None, "bughunter executable not found in PATH"

def test_bughunter_version_flag():
    result = subprocess.run(["bughunter", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert f"BugHunter v{__version__}" in result.stdout

def test_bughunter_help():
    result = subprocess.run(["bughunter", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "BugHunter CLI" in result.stdout
    assert "scan" in result.stdout
    assert "doctor" in result.stdout

def test_manifest_inclusion():
    manifest_path = Path("MANIFEST.in")
    if manifest_path.exists():
        content = manifest_path.read_text()
        assert "include README.md" in content
        assert "include LICENSE" in content
        assert "recursive-include config *.yaml" in content
