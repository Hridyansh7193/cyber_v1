import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class NucleiPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="nuclei",
            version="2.9.0",
            description="Vulnerability scanning",
            capabilities=("vulnerability_scanning",),
            supported_tools=("nuclei",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("nuclei", "-list", str(target), "-silent", "-json")

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

class NucleiWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(alive_hosts: List[str]) -> ToolResult:
        if not alive_hosts:
            return ToolResult(
                tool_name="nuclei",
                success=True,
                exit_code=0,
                stdout="",
                stderr="No alive hosts provided",
                execution_time=0.0
            )

        plugin = NucleiPlugin()
        parsed = []
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                for host in alive_hosts:
                    f.write(f"{host}\n")
                temp_path = f.name
                
            command = plugin.build_command(temp_path, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "nuclei")
            
            if exit_code == 0:
                parsed = plugin.parse(stdout, stderr)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return ToolResult(
            tool_name="nuclei",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"input_count": len(alive_hosts), "parsed_vulns": parsed}
        )
