from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_URLS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class KatanaPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="katana",
            version="1.1.0",
            description="Web crawling",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="1.0.0",
            supported_tools=("katana",),
            target_eligibility=("alive_hosts", "domain", "urls"),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return t.startswith("http://") or t.startswith("https://")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("katana")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("katana", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            cmd.append(flags["json_flag"])
            
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-list", temp_path])
        else:
            cmd.extend(["-u", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        return parsed_json, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        urls = [x.get("url", x.get("host", str(x))) if isinstance(x, dict) else str(x) for x in parsed]
        return {NEW_URLS: urls}

class KatanaWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
