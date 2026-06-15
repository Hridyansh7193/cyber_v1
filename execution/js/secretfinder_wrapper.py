"""
SecretFinder wrapper.

Purpose: Find secrets in JS files.
Input: js_files (List[str]) - Local paths or URLs to JS files.
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class SecretFinderWrapper:
    """Deterministic wrapper around the SecretFinder tool."""

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
        
        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0

        for js_file in js_files:
            # -i input, -o cli
            command = ["python3", "SecretFinder.py", "-i", js_file, "-o", "cli"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "secretfinder"
            )
            
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code

        return ToolResult(
            tool_name="secretfinder",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"input_count": len(js_files)},
        )
