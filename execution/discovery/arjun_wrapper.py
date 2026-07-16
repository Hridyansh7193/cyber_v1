from schemas.state import ExecutionState
import re
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from execution.constants import NEW_PARAMETERS

class ArjunPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="arjun",
            version="2.1.0",
            description="Parameter discovery",
            capabilities=(Capability.PARAMETER_DISCOVERY,),
            minimum_version="0.0.1",
            supported_tools=("arjun",),
            target_eligibility=("endpoints", "urls"),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        path = t.split("?")[0]
        static_exts = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ttf", ".eot", ".ico", ".html", ".htm")
        if any(path.endswith(ext) for ext in static_exts):
            return False
        return t.startswith("http://") or t.startswith("https://")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("arjun")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("arjun", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        # if flags.get("json_flag"):
        #     for f in flags["json_flag"].split():
        #         cmd.append(f)
                
        cmd.extend(["-t", "50"]) # 50 threads
        if target:
            if isinstance(target, list):
                # Arjun supports file input with -i
                import tempfile
                import os
                fd, temp_path = tempfile.mkstemp(text=True)
                with os.fdopen(fd, 'w') as f:
                    f.write("\n".join(target))
                cmd.extend(["-i", temp_path])
            else:
                cmd.extend(["-u", str(target)])
        return tuple(cmd)

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        urls = set(state.recon_state.urls)
        urls.update(state.js_state.endpoints)
        return bool(urls)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        current_target = None
        
        # Arjun stdout parsing
        # Example output:
        # [i] Target: http://example.com/
        # [+] Parameters found: id, page
        for line in stdout.splitlines():
            line = line.strip()
            if "Target:" in line:
                m = re.search(r'Target:\s+(\S+)', line)
                if m:
                    current_target = m.group(1)
            elif "Parameters found:" in line and current_target:
                m = re.search(r'Parameters found:\s+(.+)', line)
                if m:
                    params = [p.strip() for p in m.group(1).split(",")]
                    results.append({"url": current_target, "parameters": params})
        return results

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        params_discovered = []
        for res in parsed:
            url = res.get("url")
            for p in res.get("parameters", []):
                params_discovered.append(f"{url}?{p}=")
        return {NEW_PARAMETERS: params_discovered}

    def health_check(self) -> bool:
        return True
