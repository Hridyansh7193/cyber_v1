import os
import shutil
import platform
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ResolutionSource(Enum):
    CONFIGURED_PATH = "CONFIGURED_PATH"
    SYSTEM_PATH = "SYSTEM_PATH"
    NOT_FOUND = "NOT_FOUND"

class IdentityState(Enum):
    RESOLVED = "RESOLVED"
    IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    VERSION_UNSUPPORTED = "VERSION_UNSUPPORTED"
    MISSING = "MISSING"

@dataclass
class ExecutableResolution:
    tool_name: str
    requested_path: Optional[str]
    resolved_path: Optional[str]
    source: ResolutionSource
    platform: str
    exists: bool
    executable: bool
    identity_state: IdentityState
    error_code: int
    error_message: str

def _is_executable_file(path: str) -> bool:
    """Safely check if a given path is an executable file."""
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        return False
    if platform.system() != "Windows":
        return os.access(path, os.X_OK)
    return True

def resolve_executable(
    tool_name: str, 
    configured_path: Optional[str] = None
) -> ExecutableResolution:
    """
    Deterministically resolves an executable path.
    1. Checks explicitly configured_path first.
    2. Checks shutil.which(tool_name).
    3. Returns NOT_FOUND.
    """
    plat = platform.system()

    # 1. Check explicitly configured path
    if configured_path:
        expanded_path = os.path.expanduser(configured_path)
        resolved_configured = os.path.abspath(expanded_path)
        
        if _is_executable_file(resolved_configured):
            return ExecutableResolution(
                tool_name=tool_name,
                requested_path=configured_path,
                resolved_path=resolved_configured,
                source=ResolutionSource.CONFIGURED_PATH,
                platform=plat,
                exists=True,
                executable=True,
                identity_state=IdentityState.RESOLVED,
                error_code=0,
                error_message=""
            )
        else:
            # If configured path is explicitly provided but invalid, we do not fall back.
            exists = os.path.exists(resolved_configured)
            return ExecutableResolution(
                tool_name=tool_name,
                requested_path=configured_path,
                resolved_path=resolved_configured,
                source=ResolutionSource.CONFIGURED_PATH,
                platform=plat,
                exists=exists,
                executable=False,
                identity_state=IdentityState.MISSING,
                error_code=-1,
                error_message=f"Configured path '{configured_path}' is {'not executable' if exists else 'not found or not a file'}."
            )

    # 2. Check system PATH using shutil.which
    which_path = shutil.which(tool_name)
    if which_path:
        return ExecutableResolution(
            tool_name=tool_name,
            requested_path=None,
            resolved_path=which_path,
            source=ResolutionSource.SYSTEM_PATH,
            platform=plat,
            exists=True,
            executable=True,
            identity_state=IdentityState.RESOLVED,
            error_code=0,
            error_message=""
        )

    # 3. Not found
    return ExecutableResolution(
        tool_name=tool_name,
        requested_path=None,
        resolved_path=None,
        source=ResolutionSource.NOT_FOUND,
        platform=plat,
        exists=False,
        executable=False,
        identity_state=IdentityState.MISSING,
        error_code=-2,
        error_message=f"Executable '{tool_name}' not found in PATH and no explicit path configured."
    )
