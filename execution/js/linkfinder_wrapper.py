from schemas.state import ExecutionState
import tempfile
import os
import re
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_ENDPOINTS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class LinkFinderWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="linkfinder",
            version="1.0.0",
            description="Extract endpoints via LinkFinder",
            capabilities=(Capability.JS,),
            minimum_version="0.0.1",
            supported_tools=("linkfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Fallback to python linkfinder.py if not in path, but executor handles binary_path.
        # Ensure we output to JSON format in the current directory if supported, otherwise CLI
        return ("-i", state.target.resolved_url or state.target.domain, "-o", "cli")

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            # Basic parsing of LinkFinder CLI output
            # A typical LinkFinder line for cli output:
            # http://example.com/api/v1/user
            # /api/v2/config
            if line and not line.startswith("[+]") and not line.startswith("Running") and not line.startswith("Invalid input") and not line.startswith("URL:"):
                # Also avoid huge JS snippets
                if len(line) < 500:
                    results.append(line)
        return list(dict.fromkeys(results))

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_ENDPOINTS: parsed}

