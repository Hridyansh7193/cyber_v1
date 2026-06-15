"""
GraphQL wrapper.

Purpose: GraphQL endpoint discovery.
Input: urls (List[str])
Output: ToolResult
Dependencies: execution.utils.process_runner
Exceptions: Never raises — returns failed ToolResult on error.
"""
from typing import List

from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner


class GraphqlWrapper:
    """Deterministic wrapper around a GraphQL discovery tool."""

    @staticmethod
    def execute(urls: List[str]) -> ToolResult:
        if not urls:
            return ToolResult(
                tool_name="graphql_discovery",
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

        for url in urls:
            # Assuming a generic python script or tool named 'graphql_discover'
            command = ["python3", "graphql_discover.py", "-u", url]
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(
                command, "graphql_discovery"
            )
            
            all_stdout += stdout + "\n"
            all_stderr += stderr + "\n"
            total_time += execution_time
            if exit_code != 0:
                success = False
                final_exit = exit_code

        return ToolResult(
            tool_name="graphql_discovery",
            success=success,
            exit_code=final_exit,
            stdout=all_stdout.strip(),
            stderr=all_stderr.strip(),
            execution_time=total_time,
            metadata={"input_count": len(urls)},
        )
