from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping, Dict
from execution.constants import NEW_FUZZ_RESULTS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class FfufPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ffuf",
            version="2.0.0",
            description="Content discovery via ffuf",
            capabilities=(Capability.FUZZING, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("ffuf",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        wordlist = config.get("wordlist")
        cmd = ["-u", f"{state.target.resolved_url or state.target.domain}/FUZZ", "-json", "-silent"]
        if wordlist:
            cmd.extend(["-w", wordlist])
        return tuple(cmd)
    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if "results" in data:
                    results.extend(data["results"])
                else:
                    results.append(data)
            except json.JSONDecodeError:
                pass
        return results

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_FUZZ_RESULTS: parsed}

class FfufWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
