import os
from pathlib import Path
from execution.plugins.registry import REGISTRY
from runtime.workspace import WorkspaceManager

class Preflight:
    """Validates requirements specifically for an upcoming scan."""

    def validate(self, target: str, profile: str) -> bool:
        if not target:
            print("Preflight FAIL: Target is missing")
            return False
            
        # Mocking check for profile validity
        if not self._check_profile(profile):
            print(f"Preflight FAIL: Profile '{profile}' is invalid")
            return False

        # Validate write permissions
        ws = WorkspaceManager()
        if not ws.verify_integrity():
            print("Preflight FAIL: Workspace is not initialized properly")
            return False

        return True

    def _check_profile(self, profile: str) -> bool:
        # We would parse config/scan_profiles/default/{profile}.yaml
        # For now, just allow known ones
        return profile in ["minimal", "bug_bounty", "stealth", "full"]
