from execution.plugins.registry import REGISTRY
from schemas.state import ExecutionState
from schemas.target import TargetState
from datetime import datetime, timezone
import pytest

def test_subzy_command():
    plugin = REGISTRY.get_plugin("subzy")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0

def test_ffuf_command():
    plugin = REGISTRY.get_plugin("ffuf")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {"wordlist": "wordlist.txt"})
    assert len(cmd) > 0

def test_nuclei_command():
    plugin = REGISTRY.get_plugin("nuclei")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0

def test_dalfox_command():
    plugin = REGISTRY.get_plugin("dalfox")
    cmd = plugin.build_command(ExecutionState(target=TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))), {})
    assert len(cmd) > 0
