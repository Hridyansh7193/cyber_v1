"""
Subzy wrapper.

Purpose: Subdomain takeover detection via subzy.
Input: subdomains (List[str])
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
import tempfile
import os
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class SubzyWrapper:
    """Deterministic wrapper around the subzy binary."""

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

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                for sub in subdomains:
                    f.write(f"{sub}\n")
                temp_path = f.name

            command = ["subzy", "run", "--targets", temp_path, "--output", "json"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "subzy"
            )

            return ToolResult(
                tool_name="subzy",
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                metadata={"input_count": len(subdomains)},
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
