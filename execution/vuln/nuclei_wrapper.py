from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
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
            supported_tools=("nuclei",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["-silent"]
        
        # Add dynamic tags based on tech stack
        tech_tags = set()
        for tech_list in state.recon_state.tech_stack.values():
            for tech in tech_list:
                tech_tags.add(tech.lower().replace(" ", "-"))
        
        # Run generic vulnerabilities by default if no tech stack is detected, to ensure we catch basic vulns like SQLi and XSS on custom apps
        tags = ["cve", "high", "critical", "auth-bypass", "takeover", "xss", "sqli", "lfi", "rce", "misconfig", "generic"]
        if tech_tags:
            tags.extend(list(tech_tags))
            
        cmd.extend(["-tags", ",".join(tags)])
        
        # Optional: Add severity filter (allow low and info so they show up)
        cmd.extend(["-severity", "critical,high,medium,low,info"])

        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-l", temp_path])
        else:
            cmd.extend(["-u", str(target)])
        
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return results

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_NUCLEI: parsed}

class NucleiWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
