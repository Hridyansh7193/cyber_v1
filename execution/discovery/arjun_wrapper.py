from schemas.state import ExecutionState
import json
import re
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from execution.constants import NEW_PARAMETERS

class ArjunPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="arjun",
            version="2.1.0",
            description="Parameter discovery",
            capabilities=(Capability.PARAMETER_DISCOVERY,),
            minimum_version="0.0.1",
            supported_tools=("arjun",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Arjun supports -i for file input
        return ("-t", "10") # 10 threads. The target will be passed by executor

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
