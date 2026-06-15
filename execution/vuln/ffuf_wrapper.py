"""
FFUF wrapper.

Purpose: Content discovery via ffuf.
Input: target_url (str), wordlist (str)
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class FfufWrapper:
    """Deterministic wrapper around the ffuf binary."""

    @staticmethod
    def execute(target_url: str, wordlist: str) -> ToolResult:
        # Avoid hardcoding path separators, wordlist path should be provided appropriately
        command = [
            "ffuf",
            "-u", f"{target_url}/FUZZ",
            "-w", wordlist,
            "-json",
            "-silent"
        ]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(
            command, "ffuf"
        )

        return ToolResult(
            tool_name="ffuf",
            success=exit_code == 0,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"target_url": target_url, "wordlist": wordlist},
        )
