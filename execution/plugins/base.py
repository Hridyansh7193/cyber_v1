from abc import ABC, abstractmethod
from typing import Tuple, Any, Mapping
from pydantic import BaseModel, ConfigDict

from schemas.runtime import Capability
from schemas.state import ExecutionState

class PluginMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    version: str
    description: str
    capabilities: Tuple[Capability, ...]
    supported_tools: Tuple[str, ...]
    minimum_version: str | None = None
    recommended_version: str | None = None
    supported_versions: str | None = None
    required_flags: Tuple[str, ...] = tuple()
    target_eligibility: Tuple[str, ...] = tuple() # e.g., 'domain', 'url', 'js', 'api'
    supports_multi_input: bool = False
    supports_resume: bool = False

class PluginValidator(ABC):
    @abstractmethod
    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        pass

class PluginParser(ABC):
    @abstractmethod
    def parse(self, stdout: str, stderr: str) -> Any:
        pass

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        """
        DEPRECATED: Default implementation for backward compatibility.
        Plugins should override this to return semantic metadata using execution.constants.
        """
        return {"new_findings": parsed}

class PluginRunner(ABC):
    @abstractmethod
    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def self_test(self) -> "SelfTestResult":
        """Run self-tests to prove parser, command builder, and metadata generation work."""
        pass

class ExecutionPlugin(PluginValidator, PluginParser, PluginRunner, ABC):
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass

class BaseExecutionPlugin(ExecutionPlugin, ABC):
    """Standardized base execution plugin that handles boilerplate validation and health checks."""
    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def health_check(self) -> bool:
        return True
        
    def is_candidate(self, target: Any) -> bool:
        """Determines if a given target is eligible for this plugin."""
        return True
    
    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        """Override this in specific plugins to map to constants."""
        return {"new_findings": parsed}

    def self_test(self) -> "SelfTestResult":
        """Default self test for plugins. Override for specific parser testing."""
        from schemas.state import ExecutionState
        from schemas.runtime import SelfTestResult
        from services.tool_manager import ToolManager
        
        # Binary Check
        tool_name = self.metadata().name
        tm = ToolManager()
        binary = tm.available(tool_name)
        if not binary and tool_name not in ("graphql", "swagger"):
            # For pure python tools like swagger/graphql, they might be marked available differently or not needed
            binary = False
        else:
            binary = True
            
        execution = True
        # 1. Test command building
        try:
            # Mock ToolManager to bypass missing binary errors during test
            original_get_tool = tm.get_tool
            def mock_get_tool(name):
                from services.tool_manager import ToolInfo
                return ToolInfo(name=name, binary_path="/mock/path", version="99.99.99")
            tm.get_tool = mock_get_tool
            
            # Also mock CompatibilityManager to return fallback flags if version doesn't match
            from services.compatibility import CompatibilityManager
            cm = CompatibilityManager()
            original_get_flags = cm.get_flags
            def mock_get_flags(name, version):
                try:
                    return original_get_flags(name, version)
                except Exception:
                    # Fallback to first available version for test purposes
                    if "plugins" in cm._config and name in cm._config["plugins"]:
                        first_version = next(iter(cm._config["plugins"][name].get("versions", {})), None)
                        if first_version:
                            return cm._config["plugins"][name]["versions"][first_version]
                    return {"json_flag": "-json"}
            cm.get_flags = mock_get_flags
            
            from schemas.state import TargetState
            import time
            state = ExecutionState(target=TargetState(domain="example.com", session_id="test", start_time=time.time()))
            cmd = self.build_command(state, {}, target="example.com")
            if not isinstance(cmd, tuple):
                execution = False
                
            # Restore mocks
            tm.get_tool = original_get_tool
            cm.get_flags = original_get_flags
        except Exception as e:
            # Restore mocks on exception too
            tm.get_tool = original_get_tool
            if 'cm' in locals(): cm.get_flags = original_get_flags
            
            # It's okay if execution fails due to missing state. The execution test might pass if it doesn't crash on standard input
            print(f"[{tool_name}] Execution Test Failed: {repr(e)}")
            execution = False
            
        # 2. Test Parser
        parser = True
        try:
            res = self.parse("{}", "")
            if isinstance(res, tuple):
                parsed = res[0]
            else:
                parsed = res
        except Exception as e:
            print(f"[{tool_name}] Parser Test Failed: {repr(e)}")
            parser = False
            parsed = []
            
        # 3. Test Metadata
        metadata_builder = True
        try:
            meta = self.build_metadata(parsed)
            if not isinstance(meta, dict):
                metadata_builder = False
        except Exception as e:
            print(f"[{tool_name}] Metadata Builder Test Failed: {repr(e)}")
            metadata_builder = False
            
        # 4. Test Routing
        candidate_routing = True
        try:
            if not isinstance(self.is_candidate("http://example.com"), bool):
                candidate_routing = False
        except Exception:
            candidate_routing = False
            
        return SelfTestResult(
            binary=binary,
            execution=execution,
            parser=parser,
            metadata_builder=metadata_builder,
            candidate_routing=candidate_routing
        )
