from fastapi.testclient import TestClient
from api.server import app
from api.dependencies import get_scan_service
from services.scan_service import ScanService
from schemas.generated_report import GeneratedReport
from unittest.mock import Mock
import uuid

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}

def test_start_scan(monkeypatch):
    mock_scan_service = Mock(spec=ScanService)
    mock_scan_service.submit_scan.return_value = "job-123"
    
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.post("/scan", json={"domain": "example.com"})
    assert response.status_code == 200
    assert response.json()["job_id"] == "job-123"
    
    # Test validation error handling
    mock_scan_service.submit_scan.side_effect = ValueError("Invalid domain")
    response = client.post("/scan", json={"domain": "nodot"})
    assert response.status_code == 400
    
    app.dependency_overrides.clear()

def test_get_status(monkeypatch):
    mock_scan_service = Mock(spec=ScanService)
    mock_scan_service.get_status.return_value = {
        "job_id": "job-123",
        "target": "example.com",
        "status": "running",
        "progress": 50.0,
        "current_stage": "recon",
        "started_at": "2023-01-01T00:00:00Z",
        "completed_at": None,
        "error": None
    }
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.get("/status/job-123")
    assert response.status_code == 200
    assert response.json()["progress"] == 50.0
    
    mock_scan_service.get_status.return_value = None
    response = client.get("/status/invalid-job")
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

def test_get_report(monkeypatch):
    mock_scan_service = Mock(spec=ScanService)
    
    # Mock generated report
    gen_report = GeneratedReport(
        report_id=uuid.uuid4(),
        format="json",
        filename="report.json",
        mime_type="application/json",
        content='{"test": "data"}'
    )
    mock_scan_service.get_report.return_value = gen_report
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.get("/report/job-123")
    assert response.status_code == 200
    assert response.json() == {"test": "data"}
    
    mock_scan_service.get_report.return_value = None
    response = client.get("/report/invalid-job")
    assert response.status_code == 404
    
    app.dependency_overrides.clear()

def test_start_scan_with_config():
    mock_scan_service = Mock(spec=ScanService)
    mock_scan_service.submit_scan.return_value = "job-config"
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.post("/scan", json={
        "domain": "example.com",
        "config": {
            "settings": {"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
            "llm": {"provider": "dummy", "default_model": "dummy", "timeout": 30},
            "tools": {"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
            "timeouts": {"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
            "reporting": {"report_formats": ["json"], "output_directories": {}}
        }
    })
    assert response.status_code == 200
    assert response.json()["job_id"] == "job-config"
    app.dependency_overrides.clear()

def test_start_scan_exception():
    mock_scan_service = Mock(spec=ScanService)
    mock_scan_service.submit_scan.side_effect = RuntimeError("Something bad")
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.post("/scan", json={"domain": "example.com"})
    assert response.status_code == 500
    assert "Internal pipeline error" in response.json()["detail"]
    app.dependency_overrides.clear()

def test_get_report_markdown():
    mock_scan_service = Mock(spec=ScanService)
    gen_report = GeneratedReport(
        report_id=uuid.uuid4(),
        format="markdown",
        filename="report.md",
        mime_type="text/markdown",
        content="# Report Data"
    )
    mock_scan_service.get_report.return_value = gen_report
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.get("/report/job-123?format=markdown")
    assert response.status_code == 200
    assert response.text == "# Report Data"
    app.dependency_overrides.clear()

def test_cancel_scan():
    mock_scan_service = Mock(spec=ScanService)
    mock_scan_service.cancel_scan.return_value = True
    app.dependency_overrides[get_scan_service] = lambda: mock_scan_service
    
    response = client.post("/cancel/job-123")
    assert response.status_code == 200
    assert response.json()["cancelled"] is True
    
    mock_scan_service.cancel_scan.return_value = False
    response = client.post("/cancel/job-123")
    assert response.status_code == 200
    assert response.json()["cancelled"] is False
    app.dependency_overrides.clear()
