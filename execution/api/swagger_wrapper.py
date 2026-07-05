from schemas.state import ExecutionState
import json
from typing import Tuple, Any, Mapping, List
from execution.constants import NEW_SWAGGER
from execution.plugins.base import BaseExecutionPlugin, PluginMetadata
from schemas.runtime import Capability

class SwaggerPlugin(BaseExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="swagger",
            version="1.0.0",
            description="Swagger endpoint discovery",
            capabilities=(Capability.API,),
            minimum_version="0.0.1",
            supported_tools=("swagger_discover",)
        )

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        cmd = []
        if isinstance(target, list):
            if target:
                cmd.extend(["-u", str(target[0])])
        else:
            cmd.extend(["-u", str(target)])
        return tuple(cmd)

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

    def build_metadata(self, parsed: Any) -> Mapping[str, Any]:
        swagger_urls = []
        endpoints = []
        schemas = []
        for item in parsed:
            if isinstance(item, str):
                swagger_urls.append(item)
            elif isinstance(item, dict):
                if "url" in item:
                    swagger_urls.append(item["url"])
                if "endpoint" in item:
                    endpoints.append(item["endpoint"])
                if "schema" in item:
                    schemas.append(item["schema"])
        
        return {
            NEW_SWAGGER: list(dict.fromkeys(swagger_urls)),
            "new_endpoints": endpoints,
            "new_schemas": schemas
        }

class SwaggerWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
