"""
Katana wrapper.

Purpose: Web crawling via katana.
Input: alive_hosts (List[str])
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
import tempfile
import os
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class KatanaWrapper:
    """Deterministic wrapper around the katana binary."""

    @staticmethod
    def execute(alive_hosts: List[str]) -> ToolResult:
        if not alive_hosts:
            return ToolResult(
                tool_name="katana",
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
                for host in alive_hosts:
                    f.write(f"{host}\n")
                temp_path = f.name

            command = ["katana", "-list", temp_path, "-silent", "-json"]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "katana"
            )

            return ToolResult(
                tool_name="katana",
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                metadata={"input_count": len(alive_hosts)},
            )
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
