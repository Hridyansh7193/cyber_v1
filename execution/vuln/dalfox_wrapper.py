from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping, Dict
from execution.constants import NEW_DALFOX
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class DalfoxPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dalfox",
            version="2.8.0",
            description="XSS Scanning",
            capabilities=(Capability.VULN, Capability.FUZZING),
            minimum_version="0.0.1",
            supported_tools=("dalfox",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-silent", "--format", "json")

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

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

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_DALFOX: parsed}

class DalfoxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
