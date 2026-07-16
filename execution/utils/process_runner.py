import subprocess
import time
import os
import signal
import platform
import logging
import shlex
import threading
from typing import List, Tuple, Optional
from .timeout_manager import TimeoutManager
from .executable_resolver import resolve_executable, IdentityState

logger = logging.getLogger("process_runner")

_active_processes = set()
_active_processes_lock = threading.Lock()

def terminate_all_active_processes():
    """Forcefully terminates all active subprocesses. Used for emergency shutdown."""
    with _active_processes_lock:
        for process in list(_active_processes):
            try:
                if platform.system() != "Windows":
                    ProcessRunner._terminate_posix_process_tree(process)
                else:
                    ProcessRunner._terminate_windows_process_tree(process)
            except Exception:
                pass
        _active_processes.clear()

class ProcessResult:
    """
    ProcessRunner Return Contract:
    - exit_code: int (0=Success, -1=Timeout, -2=Execution Error, -3=Missing Binary, >0=Process Failed)
    - stdout: str (Decoded UTF-8, preserved even on timeout if partial output is available)
    - stderr: str (Decoded UTF-8, preserved even on timeout if partial output is available)
    - execution_time: float (Seconds the process ran)
    - binary_path: str (Resolved path used for execution)
    - command: str (Executed command)
    - cwd: str (Working directory)
    - error_message: str (Context for failures)
    - success: bool (True if exit_code == 0)
    """
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
    def _start_process(command: List[str], cwd: str) -> subprocess.Popen:
        """Starts a process in an isolated process group where supported."""
        plat = platform.system()
        
        # We use PIPE to capture stdout and stderr, but read via communicate()
        # to avoid deadlocks. This does hold output in memory. For current limits,
        # we rely on the OS pipe buffer and Python's communicate string limits.
        # Future enhancement: stream to disk if output limits are exceeded.
        kwargs = {
            "cwd": cwd,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "stdin": subprocess.DEVNULL,
            "text": False, # Capture as bytes initially to prevent decoding crash on timeout
            "shell": False,
        }

        if plat != "Windows":
            kwargs["start_new_session"] = True
        else:
            # CREATE_NEW_PROCESS_GROUP
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        return subprocess.Popen(command, **kwargs)

    @staticmethod
    def _terminate_posix_process_tree(process: subprocess.Popen) -> None:
        """Terminates a POSIX process tree gracefully using SIGTERM then SIGKILL."""
        try:
            pgid = os.getpgid(process.pid)
            os.killpg(pgid, signal.SIGTERM)
            
            # Wait grace period
            for _ in range(10):
                if process.poll() is not None:
                    return
                time.sleep(0.1)
                
            if process.poll() is None:
                os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass # Process might have already died
            
    @staticmethod
    def _terminate_windows_process_tree(process: subprocess.Popen) -> None:
        """Terminates a Windows process tree."""
        try:
            # We use process.terminate() for Windows as CTRL_BREAK_EVENT 
            # behaves differently with console vs non-console.
            # A full process tree kill on Windows might require `taskkill /T /F`
            # but for standard subprocess isolation, terminate() is the safest fallback.
            process.terminate()
            for _ in range(10):
                if process.poll() is not None:
                    return
                time.sleep(0.1)
            if process.poll() is None:
                process.kill()
        except OSError:
            pass

    @staticmethod
    def _collect_output(stdout_bytes: Optional[bytes], stderr_bytes: Optional[bytes]) -> Tuple[str, str]:
        """Safely decode bytes to UTF-8 strings."""
        stdout_str = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
        stderr_str = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""
        return stdout_str, stderr_str

    @staticmethod
    def run(command: List[str], tool_name: str, cwd: str = None, timeout: int = None) -> ProcessResult:
        """
        Executes a subprocess with retries, timeout, explicit path resolution, 
        and proper process group termination.
        """
        if timeout is None:
            timeout = TimeoutManager.get_timeout(tool_name)
        
        binary = command[0]
        
        # 1. Resolve Executable
        resolution = resolve_executable(binary)
        if not resolution.exists or not resolution.executable:
            return ProcessResult(
                exit_code=-3, stdout="", stderr="", execution_time=0.0,
                binary_path="", command=shlex.join(command), cwd=cwd or os.getcwd(),
                error_message=f"Executable '{binary}' not found or not executable."
            )

        binary_path = resolution.resolved_path
        command[0] = binary_path
        
        command_str = shlex.join(command)
        cwd_str = cwd or os.getcwd()

        max_retries = 1
        for attempt in range(max_retries + 1):
            start_time = time.time()
            process = None
            try:
                process = ProcessRunner._start_process(command, cwd_str)
                with _active_processes_lock:
                    _active_processes.add(process)
                    
                stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
                exit_code = process.returncode
                stdout, stderr = ProcessRunner._collect_output(stdout_bytes, stderr_bytes)
                error_message = ""
                
            except subprocess.TimeoutExpired as e:
                exit_code = -1
                
                # Terminate process tree
                if platform.system() != "Windows":
                    ProcessRunner._terminate_posix_process_tree(process)
                else:
                    ProcessRunner._terminate_windows_process_tree(process)
                    
                # Collect partial output if possible. 
                # communicate() after timeout/termination flushes remaining pipes.
                try:
                    partial_stdout, partial_stderr = process.communicate(timeout=2)
                    # If communicate() returned partial output, e.stdout/e.stderr is sometimes None
                    stdout_bytes = (e.stdout or b"") + (partial_stdout or b"")
                    stderr_bytes = (e.stderr or b"") + (partial_stderr or b"")
                except Exception:
                    stdout_bytes = e.stdout or b""
                    stderr_bytes = e.stderr or b""

                stdout, stderr = ProcessRunner._collect_output(stdout_bytes, stderr_bytes)
                error_message = f"Process timed out after {timeout} seconds"
                
            except KeyboardInterrupt as e:
                # Catch KeyboardInterrupt explicitly to terminate the process before re-raising
                if platform.system() != "Windows":
                    ProcessRunner._terminate_posix_process_tree(process)
                else:
                    ProcessRunner._terminate_windows_process_tree(process)
                raise e
                
            except Exception as e:
                if process and process.poll() is None:
                    try:
                        process.kill()
                    except Exception:
                        pass
                exit_code = -2
                stdout = ""
                stderr = str(e)
                error_message = f"Execution error: {str(e)}"
            finally:
                if process:
                    with _active_processes_lock:
                        _active_processes.discard(process)
                
            execution_time = time.time() - start_time
            
            if exit_code in (-1, 0, 1, 2) or attempt == max_retries:
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
