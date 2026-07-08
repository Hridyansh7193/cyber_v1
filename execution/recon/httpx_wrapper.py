from schemas.state import ExecutionState
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_HOSTS
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class HttpxPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="httpx",
            version="1.6.0",
            description="Alive host detection",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("httpx",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = ["-silent", "-json", "-title", "-tech-detect", "-rt"]
        if isinstance(target, list):
            import tempfile, os
            fd, temp_path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("\n".join(target))
            cmd.extend(["-l", temp_path])
        else:
            cmd.extend(["-u", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        return parsed_json, errors

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        hosts = []
        tech_stack = {}
        waf_detected = {}
        for x in parsed:
            if isinstance(x, dict):
                url = x.get("url", x.get("host", str(x)))
                hosts.append(url)
                techs = x.get("technologies", [])
                if techs:
                    tech_stack[url] = tuple(techs)
                    waf_keywords = ["waf", "cloudflare", "akamai", "imperva", "sucuri", "incapsula", "aws web application firewall"]
                    is_waf = any(any(wk in t.lower() for wk in waf_keywords) for t in techs)
                    if is_waf:
                        waf_detected[url] = True
            else:
                hosts.append(str(x))
        return {
            NEW_HOSTS: hosts,
            "tech_stack": tech_stack,
            "waf_detected": waf_detected
        }

class HttpxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
