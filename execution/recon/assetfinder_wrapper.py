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
            supported_tools=("assetfinder",),
            target_eligibility=("domain",),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return not t.startswith("http://") and not t.startswith("https://") and "/" not in t

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["--subs-only"]
        if isinstance(target, list):
            if target:
                cmd.append(str(target[0]))
        else:
            cmd.append(str(target))
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        lines = OutputParser.parse_lines(stdout)
        results = []
        errors = []
        for line in lines:
            if "." in line and " " not in line and not line.startswith("BANNER"):
                results.append(line)
            else:
                errors.append(f"Invalid subdomain format: {line}")
        return list(dict.fromkeys(results)), errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SUBDOMAINS: parsed}
