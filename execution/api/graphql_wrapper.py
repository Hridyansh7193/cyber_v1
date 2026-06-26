import json
from typing import List, Tuple, Any, Mapping
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

class GraphqlWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(urls: List[str]) -> ToolResult:
        if not urls:
            return ToolResult(
                tool_name="graphql_discovery",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        plugin = GraphQLPlugin()
        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0
        parsed_results = []

        for url in urls:
            command = plugin.build_command(url, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "graphql_discovery")
            
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code
            else:
                parsed_results.extend(plugin.parse(stdout, stderr))

        return ToolResult(
            tool_name="graphql_discovery",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"input_count": len(urls), "parsed_endpoints": list(dict.fromkeys(parsed_results))},
        )
