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
            supported_tools=("gau",),
            target_eligibility=("domain",),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return not t.startswith("http://") and not t.startswith("https://") and "/" not in t

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["--json"]
        if isinstance(target, list):
            # Gau takes single domains by positional argument
            if target:
                cmd.append(str(target[0]))
        else:
            cmd.append(str(target))
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        results = []
        for data in parsed_json:
            if "url" in data:
                results.append(data["url"])
        return list(dict.fromkeys(results)), errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_URLS: parsed}
