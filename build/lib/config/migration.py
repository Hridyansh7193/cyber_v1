import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigMigrator:
    """Handles migration of configuration schemas."""
    
    @staticmethod
    def get_version(config_data: Dict[str, Any]) -> str:
        return config_data.get("version", "1")

    @staticmethod
    def migrate(config_data: Dict[str, Any]) -> Dict[str, Any]:
        version = ConfigMigrator.get_version(config_data)
        
        if version == "1":
            config_data = ConfigMigrator._migrate_v1_to_v2(config_data)
            version = "2"
            
        # Add future migrations here
        
        return config_data

    @staticmethod
    def _migrate_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate version 1 to version 2 (introduces resource_limits)."""
        migrated = data.copy()
        migrated["version"] = "2"
        if "resource_limits" not in migrated:
            migrated["resource_limits"] = {
                "max_memory_mb": 4096,
                "max_runtime_seconds": 3600,
                "max_threads": 100,
                "max_subdomains": 10000,
                "max_urls": 50000,
                "max_findings": 1000
            }
        return migrated

    @staticmethod
    def migrate_file(filepath: Path) -> None:
        if not filepath.exists():
            return
            
        with open(filepath, "r") as f:
            data = yaml.safe_load(f) or {}
            
        migrated_data = ConfigMigrator.migrate(data)
        
        with open(filepath, "w") as f:
            yaml.dump(migrated_data, f, default_flow_style=False)
