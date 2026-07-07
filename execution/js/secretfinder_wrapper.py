from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from execution.constants import NEW_SECRETS
from schemas.runtime import Capability

class SecretFinderWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="secretfinder",
            version="1.0.0",
            description="Find secrets in JS files",
            capabilities=(Capability.JS, Capability.SECRETS),
            minimum_version="0.0.1",
            supported_tools=("secretfinder",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = []
        if isinstance(target, list):
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

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line and " -> " in line:
                results.append(line)
        return list(dict.fromkeys(results))

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SECRETS: parsed}
