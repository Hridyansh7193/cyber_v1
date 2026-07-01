from schemas.state import ExecutionState
import tempfile
import os
import re
import json
from typing import List, Tuple, Any, Mapping, Dict
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from execution.constants import NEW_SECRETS
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SecretFinderWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="secretfinder",
            version="1.0.0",
            description="Find secrets in JS files",
            capabilities=(Capability.JS, Capability.SECRETS),
            minimum_version="0.0.1",
            supported_tools=("secretfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-i", state.target.resolved_url or state.target.domain, "-o", "cli")

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line and " -> " in line:
                results.append(line)
        return list(dict.fromkeys(results))

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SECRETS: parsed}

