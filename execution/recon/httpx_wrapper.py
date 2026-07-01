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

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Target here can be a list of subdomains, or a file path. We will expect a file path for httpx if target is a list.
        # But to be safe, if it's a list, we will generate a temporary file in the wrapper, NOT in the plugin's build_command since build_command shouldn't have side effects.
        # Instead, we will assume target is already a file path when called from the wrapper, or we just support a file path.
        # Actually, let's just make `target` the file path.
        return ("httpx", "-l", str(target), "-silent", "-json", "-title", "-tech-detect", "-rt")

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

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        hosts = [x.get("host", x.get("url", str(x))) if isinstance(x, dict) else str(x) for x in parsed]
        return {NEW_HOSTS: hosts}

class HttpxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
