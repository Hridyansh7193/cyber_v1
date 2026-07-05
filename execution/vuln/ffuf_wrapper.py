from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_FUZZ_RESULTS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class FfufPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ffuf",
            version="2.0.0",
            description="Content discovery via ffuf",
            capabilities=(Capability.FUZZING, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("ffuf",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        # PluginExecutor passes config with 'wordlist_manager'
        wordlist_mgr = config.get("wordlist_manager")
        wordlist_path = None
        
        bughunter_config = config.get("config")
        if bughunter_config and hasattr(bughunter_config, "tools") and getattr(bughunter_config.tools, "wordlists", None):
            wordlist_path = bughunter_config.tools.wordlists.get("common")
        
        if not wordlist_path and wordlist_mgr:
            wordlist_path = wordlist_mgr.get("common")
            
        cmd = ["-json"]
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            if target:
                cmd.extend(["-u", f"{str(target[0])}/FUZZ"])
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target)) # not used
        else:
            cmd.extend(["-u", f"{str(target)}/FUZZ"])

        if wordlist_path:
            cmd.extend(["-w", wordlist_path])
        return tuple(cmd)

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

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_FUZZ_RESULTS: parsed}

class FfufWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
