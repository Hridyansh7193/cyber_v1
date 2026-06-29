import time
import functools
from typing import Callable, Any
from cli.exit_codes import SUCCESS, GENERAL_ERROR
from rich.console import Console

console = Console()

def timed_cli_command(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        exit_code = SUCCESS
        success = True
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            exit_code = getattr(e, "exit_code", GENERAL_ERROR)
            success = False
            raise e
        finally:
            duration = time.perf_counter() - start_time
            # Could log duration and exit code to telemetry/archive here
            # print(f"Command finished in {duration:.2f}s with code {exit_code}")
    return wrapper
