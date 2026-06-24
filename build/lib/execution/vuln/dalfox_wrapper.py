import tempfile
import os
from typing import List
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessRunner

class DalfoxWrapper:
    @staticmethod
    def execute(urls: List[str]) -> ToolResult:
        if not urls:
            return ToolResult(
                tool_name="dalfox",
                success=True,
                exit_code=0,
                stdout="",
                stderr="No urls provided",
                execution_time=0.0
            )
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for url in urls:
                f.write(f"{url}\n")
            temp_path = f.name
            
        command = ["dalfox", "file", temp_path, "-silent", "--format", "json"]
        exit_code, stdout, stderr, execution_time = ProcessRunner.run(command, "dalfox")
        
        os.unlink(temp_path)
        
        success = exit_code == 0
        
        return ToolResult(
            tool_name="dalfox",
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            metadata={"input_count": len(urls)}
        )
