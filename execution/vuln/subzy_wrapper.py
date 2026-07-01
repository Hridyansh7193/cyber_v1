import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping, Dict
from execution.constants import NEW_TAKEOVERS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SubzyPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="subzy",
            version="1.0.0",
            description="Subdomain takeover detection via subzy",
            capabilities=(Capability.VULN, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("subzy",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("subzy", "run", "--targets", str(target), "--output", "json")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        try:
            results = json.loads(stdout)
            if not isinstance(results, list):
                results = [results]
        except json.JSONDecodeError:
            pass
        return results

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_TAKEOVERS: parsed}

class SubzyWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
