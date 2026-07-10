from schemas.state import ExecutionState
from typing import Tuple, Any, Mapping
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
            supported_tools=("swagger_discover",),
            target_eligibility=("endpoints", "urls"),
            supports_multi_input=False
        )

    def is_candidate(self, target: Any) -> bool:
        t = str(target).lower()
        path = t.split("?")[0]
        static_exts = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ttf", ".eot", ".ico", ".html", ".htm", ".php", ".asp", ".aspx", ".jsp")
        api_keywords = ["api", "graphql", "swagger", "rest", "json", "v1", "v2", "v3", "gql"]
        if any(path.endswith(ext) for ext in static_exts) and not any(kw in t for kw in api_keywords):
            return False
        return any(kw in path for kw in api_keywords)

    def build_command(self, state: ExecutionState, config: Mapping[str, Any], target: Any = None) -> Tuple[str, ...]:
        from services.tool_manager import ToolManager
        from services.compatibility import CompatibilityManager
        
        tool_info = ToolManager().get_tool("swagger")
        version = tool_info.version if tool_info else None
        
        flags = CompatibilityManager().get_flags("swagger", version)
        
        cmd = []
        if flags.get("silent_flag"):
            cmd.append(flags["silent_flag"])
        if flags.get("json_flag"):
            # Some tools like ffuf have space-separated flags (e.g. "-o output.json -of json")
            for f in flags["json_flag"].split():
                cmd.append(f)

        if isinstance(target, list):
            if target:
                cmd.extend(["-u", str(target[0])])
        else:
            cmd.extend(["-u", str(target)])
        return tuple(cmd)

    def parse(self, stdout: str, stderr: str) -> tuple:
        from execution.utils.output_parser import OutputParser
        parsed_json, errors = OutputParser.parse_json(stdout)
        return parsed_json, errors

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
