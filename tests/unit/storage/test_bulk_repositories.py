import pytest
from storage.repositories import (
    TargetRepository, SessionRepository, SubdomainRepository, HostRepository,
    URLRepository, ParameterRepository, JSRepository, SecretRepository,
    APIRepository, FindingRepository, ReportRepository, TaskRepository, LogRepository
)
from schemas.target import TargetState
from schemas.finding import Finding, Severity, Confidence
from schemas.report import Report, ReportFormat

def test_session_create_bulk_empty(db_session):
    repo = SessionRepository()
    results = repo.create_bulk(db_session, [])
    assert len(results) == 0

def test_session_create_bulk_success(db_session):
    repo = SessionRepository()
    entities = [
        {"session_id": "bulk_sess_1", "target_domain": "example1.com"},
        {"session_id": "bulk_sess_2", "target_domain": "example2.com"}
    ]
    results = repo.create_bulk(db_session, entities)
    assert len(results) == 2
    assert results[0].session_id == "bulk_sess_1"
    assert results[1].session_id == "bulk_sess_2"
    assert results[0].status == "running"

def test_finding_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_bulk", "example.com")
    repo = FindingRepository()
    
    findings = [
        Finding(title="F1", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E1"),
        Finding(title="F2", severity=Severity.LOW, confidence=Confidence.LOW, evidence="E2")
    ]
    
    results = repo.create_bulk(db_session, "sess_bulk", findings)
    assert len(results) == 2
    assert results[0].title == "F1"
    assert results[1].title == "F2"
    
    # Check ordering
    db_results = repo.get_by_session(db_session, "sess_bulk")
    assert db_results[0].title == "F1"
    assert db_results[1].title == "F2"

def test_report_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_report", "example.com")
    repo = ReportRepository()
    reports = [
        Report(session_id="sess_report", report_path="/path/1", report_format=ReportFormat.JSON),
        Report(session_id="sess_report", report_path="/path/2", report_format=ReportFormat.MARKDOWN)
    ]
    
    results = repo.create_bulk(db_session, reports)
    assert len(results) == 2
    assert results[0].report_path == "/path/1"
    assert results[1].report_path == "/path/2"

def test_url_create_bulk_rollback(db_session):
    SessionRepository().create(db_session, "sess_url", "example.com")
    repo = URLRepository()
    
    # Intentionally cause a failure to test atomic rollback
    # url is a required field, not nullable in UrlModel. Let's force an error by missing it.
    entities = [
        {"session_id": "sess_url", "url": "https://example.com/1"},
        {"session_id": "sess_url"} # Missing required url field, should throw IntegrityError
    ]
    
    with pytest.raises(Exception): # Catch any SQLAlchemyError
        repo.create_bulk(db_session, entities)
        
    # Verify rollback
    results = repo.get_by_session(db_session, "sess_url")
    assert len(results) == 0 # First entity should not be saved

def test_target_create_bulk(db_session):
    repo = TargetRepository()
    targets = [
        TargetState(domain="example.com", session_id="1", start_time="2026-01-01T00:00:00Z"),
        TargetState(domain="test.com", session_id="2", start_time="2026-01-01T00:00:00Z")
    ]
    
    results = repo.create_bulk(db_session, targets)
    assert len(results) == 2
    assert results[0].domain == "example.com"
    assert results[1].domain == "test.com"

def test_subdomain_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_sub", "example.com")
    repo = SubdomainRepository()
    entities = [
        {"session_id": "sess_sub", "subdomain": "api.example.com", "source": "subfinder"},
        {"session_id": "sess_sub", "subdomain": "dev.example.com", "source": "amass"}
    ]
    results = repo.create_bulk(db_session, entities)
    assert len(results) == 2

def test_host_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_host", "example.com")
    repo = HostRepository()
    entities = [{"session_id": "sess_host", "url": "http://example.com"}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_api_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_api", "example.com")
    repo = APIRepository()
    entities = [{"session_id": "sess_api", "type": "swagger", "url": "http://api.com/swagger"}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_js_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_js", "example.com")
    repo = JSRepository()
    entities = [{"session_id": "sess_js", "url": "http://example.com/app.js"}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_parameter_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_param", "example.com")
    repo = ParameterRepository()
    entities = [{"session_id": "sess_param", "url": "http://example.com", "parameter": "id"}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_secret_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_secret", "example.com")
    repo = SecretRepository()
    entities = [{"session_id": "sess_secret", "type": "AWS", "value": "AKIA...", "source": "trufflehog", "confidence": "high"}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_task_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_task", "example.com")
    repo = TaskRepository()
    entities = [{"session_id": "sess_task", "task_name": "recon", "status": "pending", "attempts": 0, "duration": 0.0}]
    assert len(repo.create_bulk(db_session, entities)) == 1

def test_log_create_bulk(db_session):
    SessionRepository().create(db_session, "sess_log", "example.com")
    repo = LogRepository()
    entities = [{"session_id": "sess_log", "component": "agent", "level": "INFO", "message": "hello"}]
    assert len(repo.create_bulk(db_session, entities)) == 1
