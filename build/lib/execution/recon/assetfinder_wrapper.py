"""
Assetfinder wrapper.

Purpose: Additional subdomain discovery via assetfinder.
Input: domain (str)
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class AssetfinderWrapper:
    """Deterministic wrapper around the assetfinder binary."""

    @staticmethod
    def execute(domain: str) -> ToolResult:
        command = ["assetfinder", "--subs-only", domain]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(
            command, "assetfinder"
        )

        return ToolResult(
            tool_name="assetfinder",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"domain": domain},
        )
