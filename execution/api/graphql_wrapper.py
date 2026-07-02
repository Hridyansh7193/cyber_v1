from schemas.state import ExecutionState
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

    def build_command(self, state: ExecutionState, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("-u", state.target.resolved_url or state.target.domain)

    def validate(self, state: ExecutionState, config: Mapping[str, Any]) -> bool:
        return bool(state.target.domain)

    def parse(self, stdout: str, stderr: str) -> List[Any]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                results.append(line)
        return results

    def health_check(self) -> bool:
        return True

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        graphql_urls = []
        endpoints = []
        schemas = []
        for item in parsed:
            if isinstance(item, str):
                graphql_urls.append(item)
            elif isinstance(item, dict):
                if "url" in item:
                    graphql_urls.append(item["url"])
                if "endpoint" in item:
                    endpoints.append(item["endpoint"])
                if "schema" in item:
                    schemas.append(item["schema"])
        
        return {
            NEW_GRAPHQL: list(dict.fromkeys(graphql_urls)),
            "new_endpoints": endpoints,
            "new_schemas": schemas
        }

class GraphqlWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
