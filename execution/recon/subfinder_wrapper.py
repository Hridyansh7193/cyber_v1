"""
Subfinder wrapper.

Purpose: Subdomain enumeration via subfinder.
Input: domain (str)
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class SubfinderWrapper:
    """Deterministic wrapper around the subfinder binary."""

    @staticmethod
    def execute(domain: str) -> ToolResult:
        command = ["subfinder", "-d", domain, "-silent", "-json"]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(
            command, "subfinder"
        )

        return ToolResult(
            tool_name="subfinder",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"domain": domain},
        )
