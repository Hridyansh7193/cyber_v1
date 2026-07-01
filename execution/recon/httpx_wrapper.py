from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_HOSTS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class HttpxPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="httpx",
            version="1.6.0",
            description="Alive host detection",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("httpx",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-silent", "-json", "-title", "-tech-detect", "-rt")

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.recon_state.subdomains or state.target.domain)

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
        hosts = [x.get("host", x.get("url", str(x))) if isinstance(x, dict) else str(x) for x in parsed]
        return {NEW_HOSTS: hosts}

class HttpxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
