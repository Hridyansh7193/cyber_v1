from storage.repositories import (
    TargetRepository, SessionRepository, SubdomainRepository, HostRepository,
    URLRepository, ParameterRepository, JSRepository, SecretRepository,
    APIRepository, FindingRepository, ReportRepository, TaskRepository, LogRepository
)
from schemas.target import TargetState

def test_session_repository(db_session):
    repo = SessionRepository()
    session = repo.create(db_session, "session_123", "example.com")
    assert session.session_id == "session_123"
    assert session.target_domain == "example.com"
    assert session.status == "running"

    updated = repo.update_status(db_session, "session_123", "completed")
    assert updated.status == "completed"
    assert updated.finished_at is not None

def test_target_repository(db_session):
    repo = TargetRepository()
    target_state = TargetState(domain="example.com", session_id="123", start_time="2026-01-01T00:00:00Z")
    target = repo.create(db_session, target_state)
    assert target.domain == "example.com"

    found = repo.get_by_domain(db_session, "example.com")
    assert found is not None
    assert found.domain == "example.com"

def test_subdomain_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = SubdomainRepository()
    subdomain = repo.create(db_session, "session_123", "api.example.com", "subfinder")
    assert subdomain.subdomain == "api.example.com"

    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].subdomain == "api.example.com"

def test_host_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = HostRepository()
    host = repo.create(db_session, "session_123", "https://api.example.com", 200, "API")
    assert host.url == "https://api.example.com"
    assert host.status_code == 200

    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1

def test_url_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = URLRepository()
    repo.create(db_session, "session_123", "https://example.com/api/v1/users", "gau")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].url == "https://example.com/api/v1/users"

def test_parameter_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = ParameterRepository()
    repo.create(db_session, "session_123", "https://example.com/api", "id")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].parameter == "id"

def test_js_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = JSRepository()
    repo.create(db_session, "session_123", "https://example.com/app.js")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].url == "https://example.com/app.js"

def test_secret_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = SecretRepository()
    repo.create(db_session, "session_123", "AWS_KEY", "AKIAIOSFODNN7EXAMPLE", "trufflehog", "high")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].type == "AWS_KEY"

def test_api_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = APIRepository()
    repo.create(db_session, "session_123", "swagger", "https://example.com/swagger.json")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].type == "swagger"

def test_finding_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = FindingRepository()
    repo.create(db_session, "session_123", "XSS Found", "high", "certain", "XSS in search")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].title == "XSS Found"

def test_report_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = ReportRepository()
    repo.create(db_session, "session_123", "/tmp/report.json", "json")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].report_format == "json"

def test_task_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = TaskRepository()
    repo.create(db_session, "session_123", "recon_task", "completed", 1, 5.5)
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].task_name == "recon_task"

def test_log_repository(db_session):
    SessionRepository().create(db_session, "session_123", "example.com")
    repo = LogRepository()
    repo.create(db_session, "session_123", "recon_agent", "INFO", "Starting recon")
    
    results = repo.get_by_session(db_session, "session_123")
    assert len(results) == 1
    assert results[0].component == "recon_agent"
