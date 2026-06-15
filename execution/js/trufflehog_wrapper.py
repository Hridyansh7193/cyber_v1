"""
Trufflehog wrapper.

Purpose: Secret leakage detection.
Input: repositories (List[str]), files (List[str])
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class TrufflehogWrapper:
    """Deterministic wrapper around the trufflehog binary."""

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

        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0

        # Scan repos (git)
        for repo in repositories:
            command = ["trufflehog", "git", repo, "--json"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "trufflehog"
            )
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code

        # Scan local files (filesystem)
        for file_path in files:
            command = ["trufflehog", "filesystem", file_path, "--json"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "trufflehog"
            )
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code

        return ToolResult(
            tool_name="trufflehog",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"repos_count": len(repositories), "files_count": len(files)},
        )
