"""
LinkFinder wrapper.

Purpose: Extract endpoints via LinkFinder.
Input: js_files (List[str]) - Local paths or URLs to JS files.
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class LinkFinderWrapper:
    """Deterministic wrapper around the LinkFinder tool."""

    @staticmethod
    def execute(js_files: List[str]) -> ToolResult:
        if not js_files:
            return ToolResult(
                tool_name="linkfinder",
                success=True,
                exit_code=0,
                stdout="",
                stderr="",
                execution_time=0.0,
                metadata={"input_count": 0},
            )

        # LinkFinder typically runs against one file/url at a time.
        # We will loop and combine, or just assume it accepts multiple?
        # Actually, let's execute it iteratively and aggregate, but to stay simple
        # and deterministic we will just execute it for the first one for now, or 
        # assume the prompt expects a loop. We'll aggregate stdout.
        
        all_stdout = ""
        all_stderr = ""
        total_time = 0.0
        success = True
        final_exit = 0

        for js_file in js_files:
            # -i input, -o cli for stdout
            command = ["python3", "linkfinder.py", "-i", js_file, "-o", "cli"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "linkfinder"
            )
            
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code

        return ToolResult(
            tool_name="linkfinder",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"input_count": len(js_files)},
        )
