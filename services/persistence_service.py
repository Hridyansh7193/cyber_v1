from typing import List, Iterable
from sqlalchemy.orm import Session
from storage.database import get_db_session
from storage.repositories.finding_repository import FindingRepository
from storage.repositories.report_repository import ReportRepository
from schemas.finding import Finding
from schemas.report import Report
from storage.models import FindingModel, ReportModel

class PersistenceService:
    """Service to handle persistence of domain models using Repositories."""
    
    def __init__(self):
        self.finding_repo = FindingRepository()
        self.report_repo = ReportRepository()
        
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
