from execution.plugins.registry import REGISTRY
from schemas.state import ExecutionState
from schemas.target import TargetState
from datetime import datetime, timezone
import pytest
import os

def read_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "../../../fixtures", name)
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def test_subfinder_parser():
    plugin = REGISTRY.get_plugin("subfinder")
    out = read_fixture("subfinder.txt")
    res, _ = plugin.parse(out, "")
    assert "sub1.example.com" in res
    assert "sub2.example.com" in res

def test_subfinder_command():
    plugin = REGISTRY.get_plugin("subfinder")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0
    assert len(cmd) > 0

def test_httpx_command():
    plugin = REGISTRY.get_plugin("httpx")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0
    assert len(cmd) > 0

def test_assetfinder_command():
    plugin = REGISTRY.get_plugin("assetfinder")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0

def test_katana_command():
    plugin = REGISTRY.get_plugin("katana")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0

def test_gau_command():
    plugin = REGISTRY.get_plugin("gau")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0

