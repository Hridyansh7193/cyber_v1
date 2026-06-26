import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class DalfoxPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dalfox",
            version="2.8.0",
            description="XSS Scanning",
            capabilities=("xss_scanning",),
            supported_tools=("dalfox",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("dalfox", "file", str(target), "-silent", "--format", "json")

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

class DalfoxWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(urls: List[str]) -> ToolResult:
        if not urls:
            return ToolResult(
                tool_name="dalfox",
                success=True,
                exit_code=0,
                stdout="",
                stderr="No urls provided",
                execution_time=0.0
            )

        plugin = DalfoxPlugin()
        parsed = []
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for url in urls:
                    f.write(f"{url}\n")
                temp_path = f.name
                
            command = plugin.build_command(temp_path, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "dalfox")
            
            if exit_code == 0:
                parsed = plugin.parse(stdout, stderr)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return ToolResult(
            tool_name="dalfox",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"input_count": len(urls), "parsed_vulns": parsed}
        )
