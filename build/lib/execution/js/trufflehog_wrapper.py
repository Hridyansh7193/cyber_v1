from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.constants import NEW_SECRETS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class TrufflehogWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="trufflehog",
            version="3.0.0",
            description="Secret leakage detection",
            capabilities=(Capability.SECRETS,),
            minimum_version="0.0.1",
            supported_tools=("trufflehog",),
            target_eligibility=("js_files", "urls"),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        path = t.split("?")[0]
        return path.endswith(".js")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        # Target here could be a repo or a file path
        # Assuming config specifies type: {"mode": "git" | "filesystem"}
        mode = "filesystem"
        
        bughunter_config = config.get("config")
        
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("trufflehog")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("trufflehog", version)
        
        cmd = [mode, "--no-update"]
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
            if target and not str(target[0]).startswith("http"):
                cmd.append(str(target[0]))
            else:
                return tuple([]) # Skip execution if invalid
        else:
            target_str = str(target)
            import re
            if target_str.startswith("http://") or target_str.startswith("https://"):
                return tuple([])
            if re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", target_str):
                return tuple([])
            
            cmd.append(target_str)
            
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        return parsed_json, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        secrets = []
        for secret in parsed:
            if isinstance(secret, dict):
                secrets.append({
                    "detector": secret.get("DetectorName", "unknown"),
                    "verified": secret.get("Verified", False),
                    "redacted": secret.get("Redacted", ""),
                    "raw": secret.get("Raw", ""),
                    "file": secret.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("file", "unknown")
                })
            else:
                secrets.append({
                    "detector": "unknown",
                    "verified": False,
                    "redacted": "",
                    "raw": str(secret),
                    "file": "unknown"
                })
        return {NEW_SECRETS: secrets}
