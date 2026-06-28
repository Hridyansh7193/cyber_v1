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
        return self.root_dir / target

    def get_session_dir(self, target: str, session_id: str) -> Path:
        return self.get_target_dir(target) / "sessions" / session_id

    def create_session(self, session_id: str, target: str, profile: str) -> Path:
        """Create a new session directory and session.json."""
        import datetime
        session_dir = self.get_session_dir(target, session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create reports and logs directories for this session
        (session_dir / "reports").mkdir(exist_ok=True)
        (session_dir / "logs").mkdir(exist_ok=True)
        
        metadata = WorkspaceMetadata(
            session_id=session_id,
            target=target,
            profile=profile,
            started_at=datetime.datetime.utcnow().isoformat(),
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
