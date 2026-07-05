from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_SECRETS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class TrufflehogWrapper(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="trufflehog",
            version="3.0.0",
            description="Secret leakage detection",
            capabilities=(Capability.SECRETS,),
            minimum_version="0.0.1",
            supported_tools=("trufflehog",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        # Target here could be a repo or a file path
        # Assuming config specifies type: {"mode": "git" | "filesystem"}
        mode = "filesystem"
        
        bughunter_config = config.get("config")
        # Trufflehog mode doesn't seem to be explicitly in schemas, so fallback to filesystem
        
        cmd = [mode, "--no-update"]
        
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            # If target list is provided, we can't easily scan all of them via filesystem unless they are paths
            if target and not str(target[0]).startswith("http"):
                cmd.append(str(target[0]))
            else:
                return tuple([]) # Skip execution if invalid
        else:
            target_str = str(target)
            if target_str.startswith("http"):
                # Trufflehog filesystem doesn't support URLs, switch to git or skip
                cmd[0] = "git"
            cmd.append(target_str)
            
        return tuple(cmd)

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
