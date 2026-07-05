from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_DALFOX
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class DalfoxPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dalfox",
            version="2.8.0",
            description="XSS Scanning",
            capabilities=(Capability.VULN, Capability.FUZZING),
            minimum_version="0.0.1",
            supported_tools=("dalfox",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = []
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["file", temp_path])
        else:
            cmd.extend(["url", str(target)])
            
        cmd.extend(["--format", "json"])
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
        return {NEW_DALFOX: parsed}

class DalfoxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
