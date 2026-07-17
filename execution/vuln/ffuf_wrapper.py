from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.constants import NEW_FUZZ_RESULTS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class FfufPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ffuf",
            version="2.0.0",
            description="Content discovery via ffuf",
            capabilities=(Capability.FUZZING, Capability.HTTP, Capability.VULN),
            minimum_version="0.0.1",
            supported_tools=("ffuf",),
            target_eligibility=("alive_hosts", "domain"),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        # FFUF usually wants a host/domain
        return True

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        # PluginExecutor passes config with 'wordlist_manager'
        wordlist_mgr = config.get("wordlist_manager")
        wordlist_path = None
        
        bughunter_config = config.get("config")
        if bughunter_config and hasattr(bughunter_config, "tools") and getattr(bughunter_config.tools, "wordlists", None):
            wordlist_path = bughunter_config.tools.wordlists.get("common")
        
        if not wordlist_path and wordlist_mgr:
            wordlist_path = wordlist_mgr.get("common")
            
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("ffuf")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("ffuf", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            for f in flags["json_flag"].split():
                cmd.append(f)
        
        # Dynamic performance profile
        if bughunter_config and hasattr(bughunter_config, "profile"):
            profile_name = bughunter_config.profile.value
            if profile_name == "light":
                cmd.extend(["-t", "20", "-maxtime", "30"])
            elif profile_name == "aggressive":
                cmd.extend(["-t", "100", "-maxtime", "120"])
            else: # balanced
                cmd.extend(["-t", "50", "-maxtime", "55"])
        else:
            cmd.extend(["-t", "50", "-maxtime", "55"])
        
        # Ensure target has a scheme
        def format_target(t: Any) -> str:
            t_str = str(t)
            if not t_str.startswith("http"):
                return f"http://{t_str}"
            return t_str
            
        if isinstance(target, list):
            import tempfile
            import os
            fd, temp_path = tempfile.mkstemp(text=True)
            if target:
                base_target = format_target(target[0])
                cmd.extend(["-u", f"{base_target}/FUZZ"])
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target)) # not used
        else:
            base_target = format_target(target)
            cmd.extend(["-u", f"{base_target}/FUZZ"])

        if wordlist_path:
            cmd.extend(["-w", wordlist_path])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        results = []
        for data in parsed_json:
            if isinstance(data, dict) and "results" in data:
                results.extend(data["results"])
            else:
                results.append(data)
        return results, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_FUZZ_RESULTS: parsed}

class FfufWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
