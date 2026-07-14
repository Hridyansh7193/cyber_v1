from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
import json
from execution.constants import NEW_DALFOX
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class DalfoxPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dalfox",
            version="2.8.0",
            description="XSS Scanning",
            capabilities=(Capability.VULN, Capability.FUZZING),
            minimum_version="0.0.1",
            supported_tools=("dalfox",),
            target_eligibility=("parameters", "urls"),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return "=" in t and (t.startswith("http://") or t.startswith("https://"))

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("dalfox")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("dalfox", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            # Some tools like ffuf have space-separated flags (e.g. "-o output.json -of json")
            for f in flags["json_flag"].split():
                cmd.append(f)

        if isinstance(target, list):
            import tempfile
            import os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["file", temp_path])
        else:
            cmd.extend(["url", str(target)])
            
        cmd.extend(["--format", "json"])
        
        # Dynamic performance profile
        bughunter_config = config.get("config")
        if bughunter_config and hasattr(bughunter_config, "profile"):
            profile_name = bughunter_config.profile.value
            if profile_name == "light":
                cmd.extend(["--worker", "10", "--timeout", "10"])
            elif profile_name == "aggressive":
                cmd.extend(["--worker", "200", "--timeout", "20"])
            else: # balanced
                cmd.extend(["--worker", "20", "--timeout", "20"])
        else:
            cmd.extend(["--worker", "20", "--timeout", "20"])
        
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        """Parse both JSON-lines and the JSON array emitted by Dalfox file mode."""
        failed_requests = [
            line for line in stdout.splitlines()
            if line.lstrip().startswith("[E] Request to ") and " failed:" in line
        ]
        if failed_requests:
            return [], [
                f"Dalfox could not reach {len(failed_requests)} target(s); "
                "no vulnerability result can be trusted."
            ]

        stripped_output = stdout.strip()
        if not stripped_output:
            return [], []

        # Dalfox's `file --format json` mode emits one JSON array, often
        # pretty-printed. Parsing it a line at a time turns `[`, `,`, and `]`
        # into string records, which later violates VulnerabilityState's
        # dictionary-only contract.
        try:
            decoded = json.loads(stripped_output)
        except json.JSONDecodeError:
            decoded = None

        if decoded is not None:
            records = decoded if isinstance(decoded, list) else [decoded]
            invalid_count = sum(not isinstance(record, dict) for record in records)
            if invalid_count:
                return [], [f"Dalfox JSON contained {invalid_count} non-object record(s)."]
            return records, []

        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        records = [record for record in parsed_json if isinstance(record, dict)]
        invalid_count = len(parsed_json) - len(records)
        if invalid_count:
            errors.append(f"Dalfox JSON-lines contained {invalid_count} non-object record(s).")
        return records, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_DALFOX: parsed}

class DalfoxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
