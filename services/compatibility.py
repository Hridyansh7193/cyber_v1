import yaml
import os
from typing import Dict, Any, Optional
from schemas.errors import ErrorCode

class UnsupportedVersionError(Exception):
    pass

class CompatibilityManager:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompatibilityManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "compatibility.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

    def _match_version(self, plugin_name: str, detected_version: str) -> Optional[str]:
        if "plugins" not in self._config or plugin_name not in self._config["plugins"]:
            return None
        
        versions = self._config["plugins"][plugin_name].get("versions", {})
        
        # If no detected version, fallback to a default if available
        if not detected_version:
            # Maybe just return the first available version mapping or raise?
            return next(iter(versions)) if versions else None
            
        # Parse detected major version
        # e.g. "2.8.0" -> "2.x"
        import re
        m = re.match(r"^v?(\d+)", detected_version)
        if not m:
            return None
            
        major = m.group(1)
        expected_key = f"{major}.x"
        
        if expected_key in versions:
            return expected_key
            
        return None

    def get_flags(self, plugin_name: str, detected_version: str) -> Dict[str, str]:
        matched_key = self._match_version(plugin_name, detected_version)
        if not matched_key:
            raise UnsupportedVersionError(f"Plugin {plugin_name} version {detected_version} is unsupported.")
            
        return self._config["plugins"][plugin_name]["versions"][matched_key]

