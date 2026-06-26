import json
from typing import List, Tuple, Any, Mapping
from execution.plugins.base import ExecutionPlugin, PluginMetadata
from schemas.runtime import Capability
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class TrufflehogWrapper(ExecutionPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="trufflehog",
            version="3.0.0",
            description="Secret leakage detection",
            capabilities=(Capability.SECRETS,),
            minimum_version="0.0.1",
            supported_tools=("trufflehog",)
        )

    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        # Target here could be a repo or a file path
        # Assuming config specifies type: {"mode": "git" | "filesystem"}
        mode = config.get("mode", "filesystem")
        return ("trufflehog", mode, str(target), "--json")

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

    @staticmethod
    def execute(repositories: List[str], files: List[str]) -> ToolResult:
        if not repositories and not files:
            return ToolResult(
                tool_name="trufflehog",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"repos_count": 0, "files_count": 0},
            )

        plugin = TrufflehogWrapper()
        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0
        parsed_results = []

        for repo in repositories:
            command = plugin.build_command(repo, {"mode": "git"})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "trufflehog")
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code
            else:
                parsed_results.extend(plugin.parse(stdout, stderr))

        for file_path in files:
            command = plugin.build_command(file_path, {"mode": "filesystem"})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), "trufflehog")
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code
            else:
                parsed_results.extend(plugin.parse(stdout, stderr))

        return ToolResult(
            tool_name="trufflehog",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"repos_count": len(repositories), "files_count": len(files), "parsed_secrets": parsed_results},
        )
