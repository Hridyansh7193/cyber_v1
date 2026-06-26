import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SubzyPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="subzy",
            version="1.0.0",
            description="Subdomain takeover detection via subzy",
            capabilities=(Capability.VULN, Capability.DNS),
            minimum_version="0.0.1",
            supported_tools=("subzy",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("subzy", "run", "--targets", str(target), "--output", "json")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

    def parse(self, stdout: str, stderr: str) -> List[Mapping[str, Any]]:
        results = []
        try:
            results = json.loads(stdout)
            if not isinstance(results, list):
                results = [results]
        except json.JSONDecodeError:
            pass
        return results

    def health_check(self) -> bool:
        return True

class SubzyWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(subdomains: List[str]) -> ToolResult:
        if not subdomains:
            return ToolResult(
                tool_name="subzy",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        plugin = SubzyPlugin()
        temp_path = None
        parsed = []
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for sub in subdomains:
                    f.write(f"{sub}\n")
                temp_path = f.name

            command = plugin.build_command(temp_path, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "subzy")
            
            if exit_code == 0:
                parsed = plugin.parse(stdout, stderr)

            return ToolResult(
                tool_name="subzy",
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                metadata={"input_count": len(subdomains), "parsed_results": parsed},
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
