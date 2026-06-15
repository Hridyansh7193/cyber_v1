"""
GAU wrapper.

Purpose: Historical URL discovery via gau.
Input: domain (str)
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class GauWrapper:
    """Deterministic wrapper around the gau binary."""

    @staticmethod
    def execute(domain: str) -> ToolResult:
        command = ["gau", domain]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(
            command, "gau"
        )

        return ToolResult(
            tool_name="gau",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"domain": domain},
        )
