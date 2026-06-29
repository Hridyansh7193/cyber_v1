from typing import List, Iterable, Mapping, Any, Optional
from sqlalchemy.orm import Session
from storage.database import get_db_session
from storage.repositories.finding_repository import FindingRepository
from storage.repositories.report_repository import ReportRepository
from storage.repositories.session_repository import SessionRepository
from storage.repositories.log_repository import LogRepository
from storage.repositories.url_repository import URLRepository
from storage.repositories.subdomain_repository import SubdomainRepository
from storage.repositories.secret_repository import SecretRepository
from storage.analytics_repository import AnalyticsRepository
from schemas.finding import Finding
from schemas.report import Report
from schemas.tool_metrics import ToolMetrics
from schemas.intelligence import PlannerDecision
from storage.models import FindingModel, ReportModel, ScanSessionModel, LogModel
import json

class PersistenceService:
    """Service to handle persistence of domain models using Repositories."""
    
    def __init__(self, analytics_repo: AnalyticsRepository = None):
        self.finding_repo = FindingRepository()
        self.report_repo = ReportRepository()
        self.session_repo = SessionRepository()
        self.log_repo = LogRepository()
        self.url_repo = URLRepository()
        self.subdomain_repo = SubdomainRepository()
        self.secret_repo = SecretRepository()
        self.analytics_repo = analytics_repo or AnalyticsRepository()
        
    def _get_session(self):
        return get_db_session()
        
    def save_findings(self, session_id: str, findings: Iterable[Finding]) -> List[FindingModel]:
        """Save a batch of findings to the database."""
        with self._get_session() as db:
            return self.finding_repo.create_bulk(db, session_id, findings)
            
    def save_reports(self, reports: Iterable[Report]) -> List[ReportModel]:
        """Save a batch of reports to the database."""
        with self._get_session() as db:
            return self.report_repo.create_bulk(db, reports)

    def get_reports_for_session(self, session_id: str) -> List[ReportModel]:
        """Get all reports for a specific session."""
        with self._get_session() as db:
            return self.report_repo.get_by_session(db, session_id)

    def get_findings_for_session(self, session_id: str) -> List[FindingModel]:
        """Get all findings for a specific session."""
        with self._get_session() as db:
            return self.finding_repo.get_by_session(db, session_id)
            
    def get_all_sessions(self) -> List[ScanSessionModel]:
        """Get all scan sessions."""
        with self._get_session() as db:
            return self.session_repo.get_all(db)
            
    def create_session(self, session_id: str, target_domain: str) -> ScanSessionModel:
        """Create a new scan session."""
        with self._get_session() as db:
            return self.session_repo.create(db, session_id, target_domain)
            
    def update_session(self, session_id: str, status: str) -> Optional[ScanSessionModel]:
        """Update scan session status."""
        with self._get_session() as db:
            return self.session_repo.update_status(db, session_id, status)
            
    def get_session(self, session_id: str) -> ScanSessionModel:
        """Get a specific scan session."""
        with self._get_session() as db:
            return self.session_repo.get_by_session_id(db, session_id)
            
    def get_logs_for_session(self, session_id: str) -> List[LogModel]:
        """Get logs for a specific session."""
        with self._get_session() as db:
            return self.log_repo.get_by_session(db, session_id)
            
    def save_telemetry(self, logs: Iterable[Mapping[str, Any]]) -> None:
        """Save tool telemetry from execution state logs."""
        for log in logs:
            if log.get("type") == "tool_telemetry":
                metric = ToolMetrics(**{k: v for k, v in log.items() if k != "type"})
                self.analytics_repo.insert_metric(metric)

    def get_planner_decision(self, session_id: str) -> Optional[PlannerDecision]:
        """Extracts the PlannerDecision from the persisted state_blob of a session."""
        session = self.get_session(session_id)
        if not session or not session.state_blob:
            return None
            
        try:
            state_dict = json.loads(session.state_blob)
            intel = state_dict.get("intelligence")
            if intel and intel.get("planner"):
                return PlannerDecision(**intel["planner"])
        except Exception:
            pass
        return None

    def get_all_reports(self) -> List[ReportModel]:
        with self._get_session() as db:
            return self.report_repo.get_all(db)
            
    def get_all_findings(self) -> List[FindingModel]:
        with self._get_session() as db:
            return self.finding_repo.get_all(db)
            
    def get_all_urls(self) -> List[Any]:
        with self._get_session() as db:
            return self.url_repo.get_all(db)
            
    def get_all_subdomains(self) -> List[Any]:
        with self._get_session() as db:
            return self.subdomain_repo.get_all(db)
            
    def get_all_secrets(self) -> List[Any]:
        with self._get_session() as db:
            return self.secret_repo.get_all(db)
