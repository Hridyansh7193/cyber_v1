import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class TrufflehogWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="trufflehog",
            version="3.0.0",
            description="Secret leakage detection",
            capabilities=(Capability.SECRETS,),
            minimum_version="0.0.1",
            supported_tools=("trufflehog",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Target here could be a repo or a file path
        # Assuming config specifies type: {"mode": "git" | "filesystem"}
        mode = config.get("mode", "filesystem")
        return ("trufflehog", mode, str(target), "--json")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

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

    def health_check(self) -> bool:
        return True

