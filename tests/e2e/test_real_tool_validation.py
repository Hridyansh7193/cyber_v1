from execution.plugins.registry import REGISTRY
from schemas.state import ExecutionState
from schemas.target import TargetState
from datetime import datetime, timezone

def test_plugin_registry_loaded():
    assert len(REGISTRY.list_plugins()) > 0
    # Must have our core tools
    expected_tools = ["subfinder", "httpx", "nuclei", "dalfox"]
    for t in expected_tools:
        assert REGISTRY.get_plugin(t) is not None

def test_plugin_metadata():
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        assert isinstance(meta.name, str)
        assert meta.name != ""
        assert isinstance(meta.version, str)
        assert isinstance(meta.capabilities, tuple)
        assert isinstance(meta.supported_tools, tuple)

def test_plugin_build_command():
    plugin = REGISTRY.get_plugin("subfinder")
    target = TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=target)
    cmd = plugin.build_command(state, {})
    assert len(cmd) > 0

def test_plugin_validate():
    plugin = REGISTRY.get_plugin("subfinder")
    target = TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=target)
    assert plugin.validate(state, {}) is True
    
    empty_target = TargetState(session_id="test", domain="", start_time=datetime.now(timezone.utc))
    empty_state = ExecutionState(target=empty_target)
    assert plugin.validate(empty_state, {}) is False

def test_plugin_health_check():
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        # Assuming health_check might return True or False depending on local setup,
        # but the method should exist and return a bool.
        assert isinstance(plugin.health_check(), bool)
