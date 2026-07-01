from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping, Dict
from execution.constants import NEW_NUCLEI
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class NucleiPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="nuclei",
            version="2.9.0",
            description="Vulnerability scanning",
            capabilities=(Capability.VULN, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("nuclei",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-silent", "-json")

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
        return {NEW_NUCLEI: parsed}

class NucleiWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
