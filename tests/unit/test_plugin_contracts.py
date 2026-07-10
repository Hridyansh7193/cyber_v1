import pytest
from execution.plugins.registry import REGISTRY
from services.tool_manager import ToolManager
from schemas.runtime import Capability

@pytest.fixture(scope="module", autouse=True)
def setup_tools():
    tm = ToolManager()
    tm.detect()
    return tm

plugin_names = REGISTRY.list_plugins()

@pytest.mark.parametrize("plugin_name", plugin_names)
def test_plugin_metadata(plugin_name):
    plugin = REGISTRY.get_plugin(plugin_name)
    meta = plugin.metadata()
    
    assert meta.name, "Plugin must have a name"
    assert meta.version, "Plugin must have a version"
    assert isinstance(meta.capabilities, tuple), "Capabilities must be a tuple"
    for cap in meta.capabilities:
        assert isinstance(cap, Capability), f"Capability must be of type Capability, got {type(cap)}"
    
    assert isinstance(meta.target_eligibility, tuple), "target_eligibility must be a tuple"

@pytest.mark.parametrize("plugin_name", plugin_names)
def test_plugin_contracts(plugin_name):
    plugin = REGISTRY.get_plugin(plugin_name)
    
    # Test is_candidate
    assert isinstance(plugin.is_candidate("http://example.com"), bool), "is_candidate must return bool"
    assert isinstance(plugin.is_candidate("example.com"), bool)
    
    # Test that parse and build_metadata are callable
    assert hasattr(plugin, "parse"), "Plugin must have parse()"
    assert hasattr(plugin, "build_metadata"), "Plugin must have build_metadata()"
    assert hasattr(plugin, "build_command"), "Plugin must have build_command()"

@pytest.mark.parametrize("plugin_name", plugin_names)
def test_plugin_self_test(plugin_name):
    """
    Validates that the plugin's self_test() mechanism works.
    Even if the binary is missing, the parser, metadata_builder, execution, and candidate_routing 
    mocks MUST pass.
    """
    plugin = REGISTRY.get_plugin(plugin_name)
    
    # Run the self test
    res = plugin.self_test()
    
    if res.passed:
        assert True
    else:
        # If it failed, it MUST only be because of the missing binary.
        # The mocks for execution, parser, metadata_builder, candidate_routing MUST pass.
        assert res.execution is True, f"[{plugin_name}] Mock execution failed"
        assert res.parser is True, f"[{plugin_name}] Mock parser failed"
        assert res.metadata_builder is True, f"[{plugin_name}] Mock metadata builder failed"
        assert res.candidate_routing is True, f"[{plugin_name}] Mock candidate routing failed"
