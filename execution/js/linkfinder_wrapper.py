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
            supported_tools=("linkfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = []
        if isinstance(target, list):
            # LinkFinder doesn't easily support multiple URLs natively without a loop. We run on the first target if it's a list.
            # Realistically we should loop or use Burp crawler. We'll pick the first for now.
            if target:
                t = str(target[0])
                if not t.startswith(("http://", "https://")): t = "https://" + t
                cmd.extend(["-i", t])
        else:
            t = str(target)
            if not t.startswith(("http://", "https://")): t = "https://" + t
            cmd.extend(["-i", t])
        cmd.extend(["-o", "cli"])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("[+]") and not line.startswith("Running") and not line.startswith("Invalid input") and not line.startswith("URL:"):
                if len(line) < 500:
                    results.append(line)
        return list(dict.fromkeys(results))

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_ENDPOINTS: parsed}
