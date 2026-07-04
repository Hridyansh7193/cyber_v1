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
    def __init__(self):
        self._tools: Dict[str, ToolInfo] = {}

    def _find_binary(self, bin_name: str) -> Optional[str]:
        if bin_name in ("python", "python3"):
            return shutil.which(bin_name)
            
        # Filter out virtual environment paths to avoid resolving python packages (like httpx)
        # instead of actual system binaries (like ProjectDiscovery's httpx).
        path_env = os.environ.get("PATH", "")
        clean_paths = [p for p in path_env.split(os.pathsep) if "venv" not in p.lower()]
        
        # Ensure ~/go/bin is in the path as many Go security tools are installed there
        go_bin = os.path.expanduser("~/go/bin")
        if go_bin not in clean_paths:
            clean_paths.append(go_bin)
            
        clean_path_env = os.pathsep.join(clean_paths)
        return shutil.which(bin_name, path=clean_path_env)

    def detect(self) -> None:
        """Detect all supported tools in the environment."""
        # List of supported tools mapped to their binary names (and fallback names)
        supported_tools = {
            "subfinder": ["subfinder"],
            "httpx": ["httpx"],
            "katana": ["katana"],
            "assetfinder": ["assetfinder"],
            "gau": ["gau"],
            "linkfinder": ["python3", "python"],
            "secretfinder": ["python3", "python"],
            "nuclei": ["nuclei"],
            "dalfox": ["dalfox"],
            "swagger_discover": ["python3", "python"],
            "graphql_discover": ["python3", "python"],
            "trufflehog": ["trufflehog"],
            "ffuf": ["ffuf"],
            "subzy": ["subzy"]
        }

        for tool_name, binaries in supported_tools.items():
            path = None
            for bin_name in binaries:
                found_path = self._find_binary(bin_name)
                if found_path:
                    path = found_path
                    break
            
            if path:
                self._tools[tool_name] = ToolInfo(
                    name=tool_name,
                    binary_path=path,
                    version=None,
                    capabilities=[]
                )

    def get_tools(self) -> Dict[str, ToolInfo]:
        return self._tools.copy()

    def get_tool(self, name: str) -> Optional[ToolInfo]:
        return self._tools.get(name)

    def available(self, name: str) -> bool:
        return name in self._tools

