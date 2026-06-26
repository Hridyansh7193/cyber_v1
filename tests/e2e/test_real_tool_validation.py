import pytest
from execution.plugins.registry import REGISTRY

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
    cmd = plugin.build_command("example.com", {})
    assert "subfinder" in cmd
    assert "example.com" in cmd

def test_plugin_validate():
    plugin = REGISTRY.get_plugin("subfinder")
    assert plugin.validate("example.com", {}) is True
    assert plugin.validate("", {}) is False

def test_plugin_health_check():
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        # Assuming health_check might return True or False depending on local setup,
        # but the method should exist and return a bool.
        assert isinstance(plugin.health_check(), bool)
