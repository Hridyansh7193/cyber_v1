from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_ENDPOINTS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class LinkFinderWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="linkfinder",
            version="1.0.0",
            description="Extract endpoints via LinkFinder",
            capabilities=(Capability.JS,),
            minimum_version="0.0.1",
            supported_tools=("linkfinder",),
            target_eligibility=("js_files", "urls"),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        path = t.split("?")[0]
        return path.endswith(".js")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = []
        if isinstance(target, list):
            # LinkFinder doesn't easily support multiple URLs natively without a loop. We run on the first target if it's a list.
            # Realistically we should loop or use Burp crawler. We'll pick the first for now.
            if target:
                t = str(target[0])
                if not t.startswith(("http://", "https://")):
                    t = "https://" + t if ":443" in t else "http://" + t
                cmd.extend(["-i", t])
        else:
            t = str(target)
            if not t.startswith(("http://", "https://")):
                t = "https://" + t if ":443" in t else "http://" + t
            cmd.extend(["-i", t])
        cmd.extend(["-o", "cli"])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        lines = OutputParser.parse_lines(stdout)
        results = []
        errors = []
        
        # Check for logical errors first
        combined_output = (stdout + "\n" + stderr).lower()
        if "invalid input" in combined_output or "error" in combined_output or "timed out" in combined_output:
            for line in combined_output.splitlines():
                if "error" in line or "timed out" in line or "invalid input" in line:
                    errors.append(f"Logical error detected: {line.strip()}")
            if not results: # If we have logical errors and no results, it's a failure
                return [], errors

        for line in lines:
            if line.startswith("[+]") or line.startswith("Running") or line.startswith("Invalid input") or line.startswith("URL:") or line.startswith("BANNER"):
                continue
            if "/" in line and len(line) < 500:
                results.append(line)
            else:
                errors.append(f"Skipping potentially contaminated line: {line}")
        return list(dict.fromkeys(results)), errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_ENDPOINTS: parsed}
