import tempfile
import os
import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class SecretFinderWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="secretfinder",
            version="1.0.0",
            description="Find secrets in JS files",
            capabilities=("secret_discovery", "js_analysis"),
            supported_tools=("secretfinder",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        return ("python3", "SecretFinder.py", "-i", str(target), "-o", "cli")

    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        return bool(target)

    def parse(self, stdout: str, stderr: str) -> List[str]:
        results = []
        for line in stdout.splitlines():
            line = line.strip()
            if line and " -> " in line:
                results.append(line)
        return list(dict.fromkeys(results))

    def health_check(self) -> bool:
        return True

    @staticmethod
    def execute(js_files: List[str]) -> ToolResult:
        if not js_files:
            return ToolResult(
                tool_name="secretfinder",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        plugin = SecretFinderWrapper()
        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0
        parsed_results = []

        for js_file in js_files:
            command = plugin.build_command(js_file, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "secretfinder")
            
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code
            else:
                parsed_results.extend(plugin.parse(stdout, stderr))

        return ToolResult(
            tool_name="secretfinder",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"input_count": len(js_files), "parsed_secrets": list(dict.fromkeys(parsed_results))},
        )
