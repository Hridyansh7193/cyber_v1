from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping, List
from execution.constants import NEW_URLS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class GauWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="gau",
            version="2.1.2",
            description="Historical URL discovery",
            capabilities=(Capability.PASSIVE_RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("gau",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["--json"]
        if isinstance(target, list):
            # Gau takes single domains by positional argument
            if target:
                cmd.append(str(target[0]))
        else:
            cmd.append(str(target))
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line:
                results.append(line)
        return list(dict.fromkeys(results))

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_URLS: parsed}
