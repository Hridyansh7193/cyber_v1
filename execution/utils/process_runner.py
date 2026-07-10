import subprocess
import time
import shutil
import os
from typing import List
import logging
import shlex
from .timeout_manager import TimeoutManager

logger = logging.getLogger("process_runner")

class ProcessResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str, execution_time: float, 
                 binary_path: str = "", command: str = "", cwd: str = "", error_message: str = ""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.binary_path = binary_path
        self.command = command
        self.cwd = cwd or os.getcwd()
        self.stdout_size = len(stdout.encode('utf-8')) if stdout else 0
        self.stderr_size = len(stderr.encode('utf-8')) if stderr else 0
        self.error_message = error_message
        self.success = (exit_code == 0)

    def __iter__(self):
        yield self.exit_code
        yield self.stdout
        yield self.stderr
        yield self.execution_time

class ProcessRunner:
    @staticmethod
    def run(command: List[str], tool_name: str, cwd: str = None, timeout: int = None) -> ProcessResult:
        """
        Executes a subprocess with retries, timeout, and explicit path resolution.
        """
        if timeout is None:
            timeout = TimeoutManager.get_timeout(tool_name)
        
        binary = command[0]
        # On Windows, shutil.which handles .exe, .cmd, .bat implicitly.
        binary_path = shutil.which(binary)
        
        command_str = shlex.join(command)
        cwd_str = cwd or os.getcwd()

        if not binary_path:
            return ProcessResult(
                exit_code=-3, stdout="", stderr="", execution_time=0.0,
                binary_path="", command=command_str, cwd=cwd_str,
                error_message=f"Executable '{binary}' not found in PATH."
            )

        # Replace command[0] with absolute path to prevent ambiguity
        command[0] = binary_path

        max_retries = 1
        for attempt in range(max_retries + 1):
            start_time = time.time()
            try:
                process = subprocess.run(
                    command,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False
                )
                exit_code = process.returncode
                stdout = process.stdout
                stderr = process.stderr
                error_message = ""
            except subprocess.TimeoutExpired as e:
                exit_code = -1
                stdout = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or "")
                stderr = f"Process timed out after {timeout} seconds"
                error_message = stderr
            except subprocess.CalledProcessError as e:
                exit_code = e.returncode
                stdout = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or "")
                stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, bytes) else (e.stderr or "")
                error_message = f"Process failed with exit code {exit_code}"
            except Exception as e:
                # Catch-all to never crash the pipeline (OSError, ValueError, etc)
                exit_code = -2
                stdout = ""
                stderr = str(e)
                error_message = f"Execution error: {str(e)}"
                
            execution_time = time.time() - start_time
            
            # If successful or it's a timeout/error we shouldn't retry, break. 
            # We retry on unexpected internal failures or sometimes exit_code != 0 if desired, 
            # but usually we only retry if it was a system failure.
            # The spec says "retry policy (1 retry)". Let's retry if exit_code < 0 or if there's a crash.
            if exit_code in (0, 1, 2) or attempt == max_retries:
                break
                
            logger.warning(f"Retry {attempt + 1}/{max_retries} for {tool_name} (Exit code: {exit_code})")
            time.sleep(1) # Backoff

        return ProcessResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time=execution_time,
            binary_path=binary_path,
            command=command_str,
            cwd=cwd_str,
            error_message=error_message
        )
