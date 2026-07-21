from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
from execution.constants import NEW_URLS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class KatanaPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="katana",
            version="1.1.0",
            description="Web crawling",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="1.0.0",
            supported_tools=("katana",),
            target_eligibility=("alive_hosts", "domain"),
            supports_multi_input=True
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        return t.startswith("http://") or t.startswith("https://")

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("katana")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("katana", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            cmd.append(flags["json_flag"])
            
        # Add depth limit based on config (default to 2)
        depth = 2
        bh_config = config.get("config")
        if bh_config and hasattr(bh_config, "settings") and bh_config.settings:
            depth = bh_config.settings.scan_depth
        cmd.extend(["-depth", str(depth)])
        
        # Add crawl duration limit to prevent long hangs (default to 120 seconds)
        cmd.extend(["-crawl-duration", "120s"])
        
        # Add headless mode for SPA crawling
        cmd.extend(["-hl"])
        
        # Restrict extraction to the target's fully qualified domain name (prevents leaking to external domains like Google/OWASP)
        cmd.extend(["-fs", "fqdn"])
            
        if isinstance(target, list):
            import tempfile
            import os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-list", temp_path])
        else:
            cmd.extend(["-u", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        # Katana with -hl outputs Chromium logs to stdout which breaks JSON parsing
        clean_stdout = "\n".join(line for line in stdout.split('\n') if not line.startswith("[launcher.Browser]"))
        parsed_json, errors = OutputParser.parse_json(clean_stdout)
        # Also filter out any remaining JSONDecodeErrors that might be Katana progress logs
        filtered_errors = [e for e in errors if not (e.startswith("JSONDecodeError") and ("Progress:" in e or "Download:" in e or "Unzip:" in e))]
        return parsed_json, filtered_errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        from execution.utils.url_utils import normalize_url
        urls = []
        for x in parsed:
            clean_url = normalize_url(x)
            if clean_url:
                urls.append(clean_url)
        return {NEW_URLS: urls}

class KatanaWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
