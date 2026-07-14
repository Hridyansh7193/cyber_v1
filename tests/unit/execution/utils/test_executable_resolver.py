import os
import pytest
from unittest.mock import patch, MagicMock
from execution.utils.executable_resolver import (
    resolve_executable, 
    ResolutionSource, 
    IdentityState
)

def test_resolve_configured_valid(tmp_path):
    mock_bin = tmp_path / "mytool"
    mock_bin.touch()
    
    with patch("execution.utils.executable_resolver._is_executable_file", return_value=True):
        res = resolve_executable("mytool", str(mock_bin))
        assert res.source == ResolutionSource.CONFIGURED_PATH
        assert res.resolved_path == str(mock_bin.absolute())
        assert res.exists is True
        assert res.executable is True

def test_resolve_configured_invalid(tmp_path):
    mock_bin = tmp_path / "notfound"
    
    with patch("execution.utils.executable_resolver._is_executable_file", return_value=False):
        res = resolve_executable("mytool", str(mock_bin))
        assert res.source == ResolutionSource.CONFIGURED_PATH
        assert res.exists is False
        assert res.executable is False
        assert res.identity_state == IdentityState.MISSING
        assert res.error_code == -1

def test_resolve_system_path():
    with patch("shutil.which", return_value="/usr/bin/mytool"):
        res = resolve_executable("mytool", None)
        assert res.source == ResolutionSource.SYSTEM_PATH
        assert res.resolved_path == "/usr/bin/mytool"
        assert res.exists is True
        assert res.executable is True
        assert res.identity_state == IdentityState.RESOLVED

def test_resolve_not_found():
    with patch("shutil.which", return_value=None):
        res = resolve_executable("missingtool", None)
        assert res.source == ResolutionSource.NOT_FOUND
        assert res.resolved_path is None
        assert res.exists is False
        assert res.executable is False
        assert res.identity_state == IdentityState.MISSING
        assert res.error_code == -2
