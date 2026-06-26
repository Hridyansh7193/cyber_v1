import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class HttpxPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="httpx",
            version="1.6.0",
            description="Alive host detection",
            capabilities=("host_discovery", "tech_discovery"),
            supported_tools=("httpx",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Target here can be a list of subdomains, or a file path. We will expect a file path for httpx if target is a list.
        # But to be safe, if it's a list, we will generate a temporary file in the wrapper, NOT in the plugin's build_command since build_command shouldn't have side effects.
        # Instead, we will assume target is already a file path when called from the wrapper, or we just support a file path.
        # Actually, let's just make `target` the file path.
        return ("httpx", "-l", str(target), "-silent", "-json", "-title", "-tech-detect", "-rt")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

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

class HttpxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(subdomains: List[str]) -> ToolResult:
        if not subdomains:
            return ToolResult(
                tool_name="httpx",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        plugin = HttpxPlugin()
        temp_path = None
        parsed = []
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for sub in subdomains:
                    f.write(f"{sub}\n")
                temp_path = f.name

            command = plugin.build_command(temp_path, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "httpx")
            
            if exit_code == 0:
                parsed = plugin.parse(stdout, stderr)

            return ToolResult(
                tool_name="httpx",
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
