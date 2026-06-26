from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Optional, Any
from schemas.runtime import Capability

class InstallationManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    bughunter_version: str
    install_date: str
    python_version: str
    go_version: Optional[str]
    plugin_versions: Dict[str, str]
    installed_profiles: List[str]
    templates_version: Optional[str]
    git_commit: str

class WorkspaceMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    session_id: str
    target: str
    profile: str
    started_at: str
    completed_at: Optional[str] = None
    status: str
    report_path: Optional[str] = None
    checkpoint_id: Optional[str] = None
    runtime_ms: Optional[float] = None

class ScanManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    plugins_used: List[str]
    plugin_versions: Dict[str, str]
    runtime_ms: float
    profile: str
    skipped_nodes: List[str]
    planner_decisions: List[str]
    tool_failures: List[str]
    quality_score: float
