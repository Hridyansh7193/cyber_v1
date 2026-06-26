import pytest
from execution.plugins.registry import REGISTRY

def test_plugin_smoke():
    """Verify all plugins exist and their commands are structurally valid."""
    plugins = REGISTRY.list_plugins()
    assert len(plugins) > 0
    
    for name in plugins:
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        
        # Verify metadata
        assert meta.name == name
        assert len(meta.capabilities) > 0
        assert meta.version is not None
        
        # Verify we can build command
        cmd = plugin.build_command("example.com", {})
        assert isinstance(cmd, tuple)
        assert len(cmd) > 0
        
        # Verify health check doesn't crash (might return False if binary missing)
        assert isinstance(plugin.health_check(), bool)
