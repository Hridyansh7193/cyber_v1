from typing import List, Dict, Any
from runtime.workspace import WorkspaceManager
from schemas.generated_report import GeneratedReport
from pathlib import Path
from utils.logger import get_logger
import time

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
        
    def perform_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """Performs cleanup of temp, cache, and old logs."""
        stats = {
            "cache_files": 0,
            "cache_size_bytes": 0,
            "temp_files": 0,
            "temp_size_bytes": 0,
            "logs_deleted": 0,
            "workspace_removed": 0,
            "is_dry_run": not force,
            "elapsed_time_seconds": 0.0
        }
        
        temp_dir = self.workspace_manager.root_dir / "temp"
        
        # Calculate sizes and counts
        def get_dir_stats(d: Path):
            count, size = 0, 0
            if d.exists():
                for p in d.rglob("*"):
                    if p.is_file():
                        count += 1
                        size += p.stat().st_size
            return count, size
            
        t_count, t_size = get_dir_stats(temp_dir)
        stats["temp_files"] = t_count
        stats["temp_size_bytes"] = t_size
        
        if force:
            start = time.perf_counter()
            self.workspace_manager.clean_temp()
            stats["elapsed_time_seconds"] = time.perf_counter() - start
            
        return stats
