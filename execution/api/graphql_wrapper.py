import json
from typing import Tuple, Any, Mapping, List, Dict
from execution.constants import NEW_GRAPHQL
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class GraphQLPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="graphql_discovery",
            version="1.0.0",
            description="GraphQL endpoint discovery",
            capabilities=(Capability.API,),
            minimum_version="0.0.1",
            supported_tools=("graphql_discover",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("python3", "graphql_discover.py", "-u", str(target))

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

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
        return {NEW_GRAPHQL: parsed}

class GraphqlWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
