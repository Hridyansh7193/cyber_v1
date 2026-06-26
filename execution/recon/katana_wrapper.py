import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class KatanaPlugin(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="katana",
            version="1.1.0",
            description="Web crawling",
            capabilities=(Capability.RECON, Capability.HTTP),
            minimum_version="0.0.1",
            supported_tools=("katana",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("katana", "-list", str(target), "-silent", "-json")

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

class KatanaWrapper:
    """Deprecated: deterministic wrapper. Maintained for backward compatibility."""
    @staticmethod
    def execute(alive_hosts: List[str]) -> ToolResult:
        if not alive_hosts:
            return ToolResult(
                tool_name="katana",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        plugin = KatanaPlugin()
        temp_path = None
        parsed = []
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for host in alive_hosts:
                    f.write(f"{host}\n")
                temp_path = f.name

            command = plugin.build_command(temp_path, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "katana")
            
            if exit_code == 0:
                parsed = plugin.parse(stdout, stderr)

            return ToolResult(
                tool_name="katana",
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                metadata={"input_count": len(alive_hosts), "parsed_results": parsed},
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
