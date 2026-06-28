from typing import List
from runtime.workspace import WorkspaceManager
from schemas.generated_report import GeneratedReport
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("workspace_service")

class WorkspaceService:
    """Service for persisting rendered reports and artifacts to the filesystem."""
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager

    def save_reports(self, target: str, session_id: str, reports: List[GeneratedReport]) -> List[str]:
        """Save generated reports to the workspace session's reports directory."""
        saved_paths = []
        for report in reports:
            session_dir = self.workspace_manager.get_session_dir(target, session_id)
            reports_dir = session_dir / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = reports_dir / report.filename
            with open(file_path, "w", encoding=report.encoding) as f:
                f.write(report.content)
            saved_paths.append(str(file_path))
            logger.info(f"Saved report to: {file_path}")
        return saved_paths
