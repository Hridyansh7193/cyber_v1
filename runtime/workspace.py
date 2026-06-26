import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from schemas.manifests import WorkspaceMetadata

class WorkspaceManager:
    """Manages the BugHunter workspace layout and sessions."""
    def __init__(self, root_dir: str = "workspace"):
        self.root_dir = Path(root_dir)
        self.sessions_dir = self.root_dir / "sessions"
        self.archives_dir = self.root_dir / "archives"
        self.exports_dir = self.root_dir / "exports"
        self.reports_dir = self.root_dir / "reports"
        self.logs_dir = self.root_dir / "logs"
        self.cache_dir = self.root_dir / "cache"
        self.temp_dir = self.root_dir / "temp"

    def initialize(self) -> None:
        """Create all required workspace directories."""
        dirs = [
            self.root_dir,
            self.sessions_dir,
            self.archives_dir,
            self.exports_dir,
            self.reports_dir,
            self.logs_dir,
            self.cache_dir,
            self.temp_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def verify_integrity(self) -> bool:
        """Check if all workspace directories exist."""
        dirs = [
            self.root_dir,
            self.sessions_dir,
            self.archives_dir,
            self.exports_dir,
            self.reports_dir,
            self.logs_dir,
            self.cache_dir,
            self.temp_dir,
        ]
        return all(d.exists() and d.is_dir() for d in dirs)

    def create_session(self, session_id: str, target: str, profile: str) -> Path:
        """Create a new session directory and session.json."""
        import datetime
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        metadata = WorkspaceMetadata(
            session_id=session_id,
            target=target,
            profile=profile,
            started_at=datetime.datetime.utcnow().isoformat(),
            status="running"
        )
        
        self.update_session_metadata(session_id, metadata)
        return session_dir

    def get_session_dir(self, session_id: str) -> Path:
        return self.sessions_dir / session_id

    def update_session_metadata(self, session_id: str, metadata: WorkspaceMetadata) -> None:
        session_dir = self.get_session_dir(session_id)
        if not session_dir.exists():
            return
        
        manifest_file = session_dir / "session.json"
        with open(manifest_file, "w") as f:
            f.write(metadata.model_dump_json(indent=2))

    def get_session_metadata(self, session_id: str) -> Optional[WorkspaceMetadata]:
        manifest_file = self.get_session_dir(session_id) / "session.json"
        if not manifest_file.exists():
            return None
        with open(manifest_file, "r") as f:
            data = json.load(f)
            return WorkspaceMetadata(**data)

    def list_sessions(self) -> List[WorkspaceMetadata]:
        """List all valid sessions."""
        sessions = []
        if not self.sessions_dir.exists():
            return sessions
            
        for child in self.sessions_dir.iterdir():
            if child.is_dir():
                meta = self.get_session_metadata(child.name)
                if meta:
                    sessions.append(meta)
        return sessions

    def clean_temp(self) -> None:
        """Clean the temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir()

    def archive_session(self, session_id: str) -> str:
        """Archive a session directory into a zip file."""
        session_dir = self.get_session_dir(session_id)
        if not session_dir.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
            
        archive_path = self.archives_dir / session_id
        shutil.make_archive(str(archive_path), 'zip', str(session_dir))
        return str(archive_path) + ".zip"
