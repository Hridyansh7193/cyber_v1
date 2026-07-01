from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_URLS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class KatanaPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="katana",
            version="1.1.0",
            description="Web crawling",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("katana",)
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
        urls = [x.get("url", x.get("host", str(x))) if isinstance(x, dict) else str(x) for x in parsed]
        return {NEW_URLS: urls}

class KatanaWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
