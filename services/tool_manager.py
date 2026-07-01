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
                found_path = shutil.which(bin_name)
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

    def get_tool(self, name: str) -> Optional[ToolInfo]:
        return self._tools.get(name)

    def available(self, name: str) -> bool:
        return name in self._tools
