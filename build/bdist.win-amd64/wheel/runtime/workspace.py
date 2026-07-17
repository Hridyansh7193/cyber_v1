import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from schemas.manifests import WorkspaceMetadata

class WorkspaceManager:
    """Manages the BugHunter workspace layout and sessions."""
    def __init__(self, root_dir: str = "workspaces"):
        self.root_dir = Path(root_dir)

    def initialize(self) -> None:
        """Create root workspace directory."""
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def verify_integrity(self) -> bool:
        """Check if root workspace directory exists."""
        return self.root_dir.exists() and self.root_dir.is_dir()

    def get_target_dir(self, target: str) -> Path:
        from utils.target_utils import sanitize_workspace_target
        target = sanitize_workspace_target(target)
        target_path = (self.root_dir / target).resolve()
        if not target_path.is_relative_to(self.root_dir.resolve()):
            raise ValueError(f"Path traversal detected in target: {target}")
        return target_path

    def get_session_dir(self, target: str, session_id: str) -> Path:
        target_dir = self.get_target_dir(target)
        # Ensure session_id doesn't cause path traversal
        session_id_safe = Path(session_id).name
        session_path = (target_dir / "sessions" / session_id_safe).resolve()
        if not session_path.is_relative_to(target_dir.resolve()):
            raise ValueError(f"Path traversal detected in session_id: {session_id}")
        return session_path

    def create_session(self, session_id: str, target: str, profile: str) -> Path:
        """Create a new session directory and session.json."""
        import datetime
        session_dir = self.get_session_dir(target, session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create reports, logs, and evidence directories for this session
        (session_dir / "reports").mkdir(exist_ok=True)
        (session_dir / "logs").mkdir(exist_ok=True)
        evidence_dir = session_dir / "evidence"
        evidence_dir.mkdir(exist_ok=True)
        (evidence_dir / "raw").mkdir(exist_ok=True)
        (evidence_dir / "parsed").mkdir(exist_ok=True)
        (evidence_dir / "telemetry").mkdir(exist_ok=True)
        (evidence_dir / "plugin").mkdir(exist_ok=True)
        
        metadata = WorkspaceMetadata(
            session_id=session_id,
            target=target,
            profile=profile,
            started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            status="running"
        )
        
        self.update_session_metadata(target, session_id, metadata)
        return session_dir

    def update_session_metadata(self, target: str, session_id: str, metadata: WorkspaceMetadata) -> None:
        session_dir = self.get_session_dir(target, session_id)
        if not session_dir.exists():
            return
        
        manifest_file = session_dir / "session.json"
        with open(manifest_file, "w") as f:
            f.write(metadata.model_dump_json(indent=2))

    def get_session_metadata(self, target: str, session_id: str) -> Optional[WorkspaceMetadata]:
        manifest_file = self.get_session_dir(target, session_id) / "session.json"
        if not manifest_file.exists():
            return None
        with open(manifest_file, "r") as f:
            data = json.load(f)
            return WorkspaceMetadata(**data)

    def list_sessions(self, target: str) -> List[WorkspaceMetadata]:
        """List all valid sessions for a target."""
        sessions = []
        target_sessions_dir = self.get_target_dir(target) / "sessions"
        if not target_sessions_dir.exists():
            return sessions
            
        for child in target_sessions_dir.iterdir():
            if child.is_dir():
                meta = self.get_session_metadata(target, child.name)
                if meta:
                    sessions.append(meta)
        return sessions

    def clean_temp(self) -> None:
        """Clean the temporary directory (global temp)."""
        temp_dir = self.root_dir / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(exist_ok=True)

    def archive_session(self, target: str, session_id: str) -> str:
        """Archive a session directory into a zip file."""
        session_dir = self.get_session_dir(target, session_id)
        if not session_dir.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
            
        archives_dir = self.get_target_dir(target) / "archives"
        archives_dir.mkdir(exist_ok=True)
        archive_path = archives_dir / session_id
        shutil.make_archive(str(archive_path), 'zip', str(session_dir))
        return str(archive_path) + ".zip"

    def list_all_sessions(self) -> List[WorkspaceMetadata]:
        """List all valid sessions across all targets."""
        sessions = []
        if not self.root_dir.exists():
            return sessions
        for target_dir in self.root_dir.iterdir():
            if target_dir.is_dir() and target_dir.name != "temp":
                sessions.extend(self.list_sessions(target_dir.name))
        return sessions

    def get_workspace_stats(self) -> Dict[str, Any]:
        """Calculate statistics about the workspace (counts and sizes)."""
        stats = {
            "targets": 0,
            "sessions": 0,
            "reports": 0,
            "logs": 0,
            "total_size_bytes": 0
        }
        if not self.root_dir.exists():
            return stats

        for target_dir in self.root_dir.iterdir():
            if target_dir.is_dir() and target_dir.name != "temp":
                stats["targets"] += 1
                sessions_dir = target_dir / "sessions"
                if sessions_dir.exists():
                    for session_dir in sessions_dir.iterdir():
                        if session_dir.is_dir():
                            stats["sessions"] += 1
                            reports_dir = session_dir / "reports"
                            if reports_dir.exists():
                                stats["reports"] += len(list(reports_dir.iterdir()))
                            logs_dir = session_dir / "logs"
                            if logs_dir.exists():
                                stats["logs"] += len(list(logs_dir.iterdir()))

        def get_size(start_path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
            return total_size

        stats["total_size_bytes"] = get_size(str(self.root_dir))
        return stats
