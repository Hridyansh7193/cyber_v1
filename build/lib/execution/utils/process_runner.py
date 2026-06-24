import subprocess
import time
from typing import List, Dict, Any, Tuple
import logging
from .timeout_manager import TimeoutManager

logger = logging.getLogger("process_runner")

class ProcessRunner:
    @staticmethod
    def run(command: List[str], tool_name: str, cwd: str = None) -> Tuple[int, str, str, float]:
        """
        Executes a subprocess and returns exit_code, stdout, stderr, execution_time.
        """
        timeout = TimeoutManager.get_timeout(tool_name)
        start_time = time.time()
        
        try:
            process = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            exit_code = process.returncode
            stdout = process.stdout
            stderr = process.stderr
        except subprocess.TimeoutExpired as e:
            exit_code = -1
            stdout = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = f"Process timed out after {timeout} seconds"
        except subprocess.CalledProcessError as e:
            exit_code = e.returncode
            stdout = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else (e.stderr or "")
        except OSError as e:
            exit_code = -2
            stdout = ""
            stderr = str(e)
            
        execution_time = time.time() - start_time
        return exit_code, stdout, stderr, execution_time
