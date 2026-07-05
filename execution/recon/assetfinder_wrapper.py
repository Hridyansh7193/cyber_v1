from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping, List
from execution.constants import NEW_SUBDOMAINS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class AssetfinderWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="assetfinder",
            version="0.1.1",
            description="Subdomain discovery via assetfinder",
            capabilities=(Capability.PASSIVE_RECON, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("assetfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["--subs-only"]
        if isinstance(target, list):
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
        return {NEW_SUBDOMAINS: parsed}
