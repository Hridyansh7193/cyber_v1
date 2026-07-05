from schemas.state import ExecutionState
import json
from typing import Tuple, Any, Mapping, List
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
            supported_tools=("subfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["-silent", "-json"]
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-dL", temp_path])
        else:
            cmd.extend(["-d", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "host" in data:
                    results.append(data["host"])
            except json.JSONDecodeError:
                if "." in line and " " not in line:
                    results.append(line)
        return list(dict.fromkeys(results))

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SUBDOMAINS: parsed}
