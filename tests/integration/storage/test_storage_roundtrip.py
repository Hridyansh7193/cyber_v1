from datetime import datetime, timezone
from storage.repositories.target_repository import TargetRepository
from storage.repositories.finding_repository import FindingRepository
from storage.repositories.report_repository import ReportRepository
from storage.repositories.task_repository import TaskRepository
from storage.repositories.session_repository import SessionRepository

from schemas.target import TargetState
from schemas.finding import Finding
from schemas.task import Task
from uuid import uuid4

from storage.models import Base

def test_storage_roundtrip_integrity(tmp_path):
    from sqlalchemy import create_engine
    test_db_path = tmp_path / "roundtrip.db"
    test_engine = create_engine(f"sqlite:///{test_db_path}")
    Base.metadata.create_all(bind=test_engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    with SessionLocal() as session:
        target_repo = TargetRepository()
        finding_repo = FindingRepository()
        report_repo = ReportRepository()
        task_repo = TaskRepository()
        session_repo = SessionRepository()
        
        session_id = "test_roundtrip_session"
        domain = "roundtrip.example.com"
        
        # Target Roundtrip
        target = TargetState(domain=domain, scope=(domain,), session_id=session_id, start_time=datetime.now(timezone.utc))
        target_repo.create(session, target)
        retrieved_target = target_repo.get_by_domain(session, domain)
        assert retrieved_target.domain == target.domain
        
        # Session Roundtrip (Since Target creates a session inherently or we create one explicitly?)
        # Let's create session directly
        session_obj = session_repo.create(session, session_id, domain)
        retrieved_session = session_repo.get_by_session_id(session, session_id)
        assert retrieved_session.session_id == session_id
        
        # Finding Roundtrip
        finding = Finding(title="XSS", severity="high", confidence="certain", evidence="payload")
        finding_repo.create_bulk(session, session_id, [finding])
        retrieved_findings = finding_repo.get_by_session(session, session_id)
        assert any(f.title == finding.title for f in retrieved_findings)
        
        # Report Roundtrip
        from schemas.report import Report, ReportFormat
        report_schema = Report(report_id=uuid4(), session_id=session_id, report_path="test.md", report_format=ReportFormat.MARKDOWN)
        report_repo.create_bulk(session, [report_schema])
        retrieved_reports = report_repo.get_by_session(session, session_id)
        assert any(r.report_path == "test.md" for r in retrieved_reports)
        
        # Task Roundtrip
        task = Task(name="recon", status="in_progress")
        task_repo.create_bulk(session, [{"session_id": session_id, "task_name": task.name, "status": task.status.value}])
        retrieved_tasks = task_repo.get_by_session(session, session_id)
        assert any(t.task_name == task.name for t in retrieved_tasks)
        
        # Verify model_dump matching conceptual fields
        dumped_finding = finding.model_dump()
        assert dumped_finding["title"] == retrieved_findings[0].title
