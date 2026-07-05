from schemas.state import ExecutionState
import json
import tempfile
import os
from typing import List, Tuple, Any, Mapping, Dict
from execution.constants import NEW_SECRETS
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

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Target here could be a repo or a file path
        # Assuming config specifies type: {"mode": "git" | "filesystem"}
        mode = config.get("mode", "filesystem")
        return (mode, "--no-update")

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
        secrets = []
        for secret in parsed:
            secrets.append({
                "detector": secret.get("DetectorName", "unknown"),
                "verified": secret.get("Verified", False),
                "redacted": secret.get("Redacted", ""),
                "raw": secret.get("Raw", ""),
                "file": secret.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("file", "unknown")
            })
        return {NEW_SECRETS: secrets}

