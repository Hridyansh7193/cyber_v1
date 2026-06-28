from typing import List
from runtime.workspace import WorkspaceManager
from schemas.generated_report import GeneratedReport
from pathlib import Path

class WorkspaceService:
    """Service for persisting rendered reports and artifacts to the filesystem."""
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager

    def save_reports(self, session_id: str, reports: List[GeneratedReport]) -> List[str]:
        """Save generated reports to the workspace reports directory."""
        saved_paths = []
        for report in reports:
            file_path = self.workspace_manager.reports_dir / report.filename
            with open(file_path, "w", encoding=report.encoding) as f:
                f.write(report.content)
            saved_paths.append(str(file_path))
        print("Saving to:", file_path)
        return saved_paths
