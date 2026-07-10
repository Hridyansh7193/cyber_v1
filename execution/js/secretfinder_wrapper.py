from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from execution.constants import NEW_SECRETS
from schemas.runtime import Capability

class SecretFinderWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="secretfinder",
            version="1.0.0",
            description="Find secrets in JS files",
            capabilities=(Capability.JS, Capability.SECRETS),
            minimum_version="0.0.1",
            supported_tools=("secretfinder",),
            target_eligibility=("js_files", "urls"),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        path = t.split("?")[0]
        return path.endswith(".js")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("secretfinder")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("secretfinder", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            # Some tools like ffuf have space-separated flags (e.g. "-o output.json -of json")
            for f in flags["json_flag"].split():
                cmd.append(f)

        if isinstance(target, list):
            if target:
                t = str(target[0])
                if not t.startswith(("http://", "https://")):
                    t = "https://" + t if ":443" in t else "http://" + t
                cmd.extend(["-i", t])
        else:
            t = str(target)
            if not t.startswith(("http://", "https://")):
                t = "https://" + t if ":443" in t else "http://" + t
            cmd.extend(["-i", t])
        cmd.extend(["-o", "cli"])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        results = []
        errors = []
        
        # Check for logical errors first
        combined_output = (stdout + "\n" + stderr).lower()
        if "max retries exceeded" in combined_output or "connectiontimeout" in combined_output or "error" in combined_output:
            for line in combined_output.splitlines():
                if "error" in line or "max retries" in line or "timeout" in line:
                    errors.append(f"Logical error detected: {line.strip()}")
            if not results: # If we have logical errors and no results, it's a failure
                return [], errors

        for line in stdout.splitlines():
            line = line.strip()
            if line and " -> " in line:
                results.append(line)
        return list(dict.fromkeys(results)), errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SECRETS: parsed}
