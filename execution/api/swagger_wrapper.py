from schemas.state import ExecutionState
import json
from typing import Tuple, Any, Mapping, List, Dict
from execution.constants import NEW_SWAGGER
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SwaggerPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="swagger",
            version="1.0.0",
            description="Swagger endpoint discovery",
            capabilities=(Capability.API,),
            minimum_version="0.0.1",
            supported_tools=("swagger_discover",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-u", state.target.resolved_url or state.target.domain)

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line:
                results.append(line)
        return list(dict.fromkeys(results))

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        return {NEW_SWAGGER: parsed}

class SwaggerWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
