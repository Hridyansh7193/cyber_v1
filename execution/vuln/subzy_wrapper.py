from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_TAKEOVERS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class SubzyPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="subzy",
            version="1.0.0",
            description="Subdomain takeover detection via subzy",
            capabilities=(Capability.VULN, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("subzy",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["run", "--hide_fails"]
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["--targets", temp_path])
        else:
            cmd.extend(["--target", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        try:
            results = json.loads(stdout)
            if not isinstance(results, list):
                results = [results]
        except json.JSONDecodeError:
            pass
        return results

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_TAKEOVERS: parsed}

class SubzyWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
