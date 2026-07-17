from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.constants import NEW_NUCLEI
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class NucleiPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="nuclei",
            version="2.9.0",
            description="Vulnerability scanning",
            capabilities=(Capability.VULN, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("nuclei",),
            target_eligibility=("urls", "alive_hosts", "endpoints"),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return t.startswith("http://") or t.startswith("https://")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("nuclei")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("nuclei", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            # Some tools like ffuf have space-separated flags (e.g. "-o output.json -of json")
            for f in flags["json_flag"].split():
                cmd.append(f)

        
        # Add dynamic tags based on tech stack
        tech_tags = set()
        for tech_list in state.recon_state.tech_stack.values():
            for tech in tech_list:
                tech_tags.add(tech.lower().replace(" ", "-"))
        
        # Run default templates to ensure we catch basic vulns
        tags = ["cve", "high", "critical", "auth-bypass", "takeover", "xss", "sqli", "lfi", "rce", "misconfig"]
        if tech_tags:
            tags.extend(list(tech_tags))
        cmd.extend(["-tags", ",".join(tags)])
        
        # Optional: Add severity filter (allow low and info so they show up)
        cmd.extend(["-severity", "critical,high,medium,low,info"])
        
        # Dynamic performance profile
        bughunter_config = config.get("config")
        if bughunter_config and hasattr(bughunter_config, "profile"):
            profile_name = bughunter_config.profile.value
            if profile_name == "light":
                cmd.extend(["-c", "20", "-rl", "50"])
            elif profile_name == "aggressive":
                cmd.extend(["-c", "100", "-rl", "300"])
            else: # balanced
                cmd.extend(["-c", "50", "-rl", "150"])
        else:
            cmd.extend(["-c", "50", "-rl", "150"])

        if isinstance(target, list):
            import tempfile
            import os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-l", temp_path])
        else:
            cmd.extend(["-u", str(target)])
        
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        return parsed_json, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_NUCLEI: parsed}

class NucleiWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
