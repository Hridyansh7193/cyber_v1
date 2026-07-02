from schemas.state import ExecutionState
import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.constants import NEW_HOSTS
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class HttpxPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="httpx",
            version="1.6.0",
            description="Alive host detection",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("httpx",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-silent", "-json", "-title", "-tech-detect", "-rt")

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.recon_state.subdomains or state.target.domain)

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

    def health_check(self) -> bool:
        return True

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
