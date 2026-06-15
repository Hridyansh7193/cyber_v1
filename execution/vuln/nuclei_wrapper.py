import tempfile
import os
from typing import List
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class NucleiWrapper:
    @staticmethod
    def execute(alive_hosts: List[str]) -> ToolResult:
        if not alive_hosts:
            return ToolResult(
                tool_name="nuclei",
                success=True,
                exit_code=0,
                stdout="",
                stderr="No alive hosts provided",
                execution_time=0.0
            )
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for host in alive_hosts:
                f.write(f"{host}\n")
            temp_path = f.name
            
        command = ["nuclei", "-list", temp_path, "-silent", "-json"]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(command, "nuclei")
        
        os.unlink(temp_path)
        
        success = exit_code == 0
        
        return ToolResult(
            tool_name="nuclei",
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"input_count": len(alive_hosts)}
        )
