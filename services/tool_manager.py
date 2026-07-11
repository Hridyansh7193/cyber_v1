import os
import shutil
from typing import Dict, List, Optional
from pydantic import BaseModel

class ToolInfo(BaseModel):
    name: str
    binary_path: str
    version: Optional[str] = None
    capabilities: List[str] = []

class ToolManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolManager, cls).__new__(cls)
            cls._instance._tools = {}
            cls._instance.detect()
        return cls._instance
        
    def _find_binary(self, bin_name: str) -> Optional[str]:
        if bin_name in ("python", "python3"):
            return shutil.which(bin_name)
            
        # Hardcode explicit Python script paths for custom wrappers
        custom_scripts = {
            "linkfinder.py": os.path.expanduser("~/tools/LinkFinder/linkfinder.py"),
            "SecretFinder.py": os.path.expanduser("~/tools/SecretFinder/SecretFinder.py"),
            "swagger_discovery.py": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "execution", "api", "swagger_discovery.py")),
            "graphql_discovery.py": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "execution", "api", "graphql_discovery.py")),
        }
        
        if bin_name in custom_scripts:
            # Verify if it exists before returning it
            if os.path.exists(custom_scripts[bin_name]):
                return custom_scripts[bin_name]
            return None

        # Filter out virtual environment paths to avoid resolving python packages (like httpx)
        # instead of actual system binaries (like ProjectDiscovery's httpx).
        path_env = os.environ.get("PATH", "")
        clean_paths = []
        for p in path_env.split(os.pathsep):
            p_lower = p.lower()
            if "venv" not in p_lower and ".venv" not in p_lower:
                clean_paths.append(p)
        
        # Ensure ~/go/bin is at the very front of the path as many Go security tools are installed there
        go_bin = os.path.expanduser("~/go/bin")
        if go_bin in clean_paths:
            clean_paths.remove(go_bin)
        clean_paths.insert(0, go_bin)
            
        clean_path_env = os.pathsep.join(clean_paths)
        
        # On Linux/macOS, if the binary is specifically in ~/go/bin, shutil.which with custom path will find it
        return shutil.which(bin_name, path=clean_path_env)

    def _detect_version(self, path: str, tool_name: str) -> Optional[str]:
        import subprocess
        import re
        
        for flag in ["-version", "--version", "version"]:
            cmd = [path, flag]
            if path.endswith(".py"):
                cmd = ["python3", path, flag]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                out = res.stdout + res.stderr
                if out:
                    # Look for standalone version strings, avoid IPs like 127.0.0.1
                    m = re.search(r"(?<![\d.])v?(\d+\.\d+\.\d+(?:-\w+)?)(?![\d.])", out)
                    if m:
                        return m.group(1)
            except Exception:
                pass
        return None

    def detect(self) -> None:
        """Detect all supported tools in the environment."""
        # List of supported tools mapped to their binary names (and fallback names)
        supported_tools = {
            "subfinder": ["subfinder"],
            "httpx": ["httpx"],
            "katana": ["katana"],
            "assetfinder": ["assetfinder"],
            "gau": ["gau"],
            "linkfinder": ["linkfinder.py", "linkfinder"],
            "secretfinder": ["SecretFinder.py", "secretfinder.py", "secretfinder"],
            "nuclei": ["nuclei"],
            "dalfox": ["dalfox"],
            "swagger_discover": ["swagger_discovery.py", "swagger_discover", "swagger_discover.py"],
            "graphql_discover": ["graphql_discovery.py", "graphql_discover", "graphql_discover.py"],
            "trufflehog": ["trufflehog"],
            "ffuf": ["ffuf"],
            "subzy": ["subzy"],
            "arjun": ["arjun"]
        }

        for tool_name, binaries in supported_tools.items():
            path = None
            for bin_name in binaries:
                found_path = self._find_binary(bin_name)
                if found_path:
                    path = found_path
                    break
            
            if path:
                version = self._detect_version(path, tool_name)
                self._tools[tool_name] = ToolInfo(
                    name=tool_name,
                    binary_path=path,
                    version=version,
                    capabilities=[]
                )

    def get_tools(self) -> Dict[str, ToolInfo]:
        return self._tools.copy()

    def get_tool(self, name: str) -> Optional[ToolInfo]:
        return self._tools.get(name)

    def available(self, name: str) -> bool:
        return name in self._tools

