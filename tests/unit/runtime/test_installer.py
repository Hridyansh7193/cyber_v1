import pytest
import os
from pathlib import Path
from runtime.installer import Installer

def test_installer_dry_run():
    installer = Installer()
    summary = installer.install(dry_run=True)
    assert summary.success is True
    assert len(summary.results) == 0
    assert not Path(".install.lock").exists()

def test_installer_execution():
    installer = Installer()
    # Ensure lock file is cleared
    if Path(".install.lock").exists():
        Path(".install.lock").unlink()
        
    summary = installer.install(dry_run=False)
    assert summary.success is True
    assert len(summary.results) > 0
    assert Path("installation.json").exists()
    assert not Path(".install.lock").exists()
