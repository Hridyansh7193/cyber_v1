import json
from typing import Tuple, Any, Mapping, List
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SubfinderWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="subfinder",
            version="2.6.6",
            description="Subdomain enumeration via subfinder",
            capabilities=(Capability.RECON, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("subfinder",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("subfinder", "-d", str(target), "-silent", "-json")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

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

    def health_check(self) -> bool:
        return True

