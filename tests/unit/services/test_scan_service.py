import pytest
from unittest.mock import Mock
from services.scan_service import ScanService
from services.job_registry import JobRegistry, JobStatus
from services.orchestrator_adapter import OrchestratorAdapter
from config.schemas import BugHunterConfig

def test_scan_service_submit_scan():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    registry = JobRegistry()
    scan_service = ScanService(mock_adapter, registry)
    
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    
    mock_adapter.get_status.return_value = {"status": "PENDING", "target_domain": "example.com"}
    job_id = scan_service.submit_scan("example.com", config)
    assert job_id is not None
    
    status = scan_service.get_status(job_id)
    assert status["status"] == "PENDING"
    assert status["target_domain"] == "example.com"

def test_scan_service_cancel_job():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    registry = JobRegistry()
    scan_service = ScanService(mock_adapter, registry)
    
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    
    job_id = scan_service.submit_scan("example.com", config)
    
    mock_adapter.cancel.return_value = True
    result = scan_service.cancel_scan(job_id)
    assert result is True
    
    mock_adapter.get_status.return_value = {"status": "CANCELLED"}
    status = scan_service.get_status(job_id)
    assert status["status"] == "CANCELLED"

def test_scan_service_invalid_job():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    registry = JobRegistry()
    scan_service = ScanService(mock_adapter, registry)
    
    mock_adapter.get_status.return_value = None
    status = scan_service.get_status("invalid-id")
    assert status is None
    
    mock_adapter.cancel.return_value = False
    result = scan_service.cancel_scan("invalid-id")
    assert result is False
