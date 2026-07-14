from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.constants import NEW_SUBDOMAINS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class SubfinderWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="subfinder",
            version="2.6.6",
            description="Subdomain enumeration via subfinder",
            capabilities=(Capability.PASSIVE_RECON, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("subfinder",),
            target_eligibility=("domain",),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return not t.startswith("http://") and not t.startswith("https://") and "/" not in t

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("subfinder")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("subfinder", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            cmd.append(flags["json_flag"])
            
        if isinstance(target, list):
            import tempfile
            import os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-dL", temp_path])
        else:
            cmd.extend(["-d", str(target)])
            
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        results = []
        for data in parsed_json:
            if isinstance(data, dict) and "host" in data:
                results.append(data["host"])
            elif isinstance(data, str) and "." in data and " " not in data:
                results.append(data)
        return list(dict.fromkeys(results)), errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SUBDOMAINS: parsed}
