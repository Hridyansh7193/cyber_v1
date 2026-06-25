import pytest
from unittest.mock import Mock
import uuid
from services.report_service import ReportService
from services.orchestrator_adapter import OrchestratorAdapter
from schemas.report import Report, ReportFormat

def test_report_service_get_report_success():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    
    report_id = uuid.uuid4()
    db_report = Report(
        report_id=report_id,
        session_id="job-123",
        report_format=ReportFormat.JSON
    )
    
    mock_adapter.get_report.return_value = [db_report]
    report_service = ReportService(mock_adapter)
    
    report = report_service.get_report("job-123", "json")
    assert report is not None
    assert "job-123" in report.content
    mock_adapter.get_report.assert_called_once_with("job-123")

def test_report_service_get_report_missing():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    mock_adapter.get_report.return_value = []
    
    report_service = ReportService(mock_adapter)
    report = report_service.get_report("job-123", "json")
    
    assert report is None
    mock_adapter.get_report.assert_called_once_with("job-123")

def test_report_service_get_report_exception():
    mock_adapter = Mock(spec=OrchestratorAdapter)
    mock_adapter.get_report.side_effect = RuntimeError("Storage connection failed")
    
    report_service = ReportService(mock_adapter)
    with pytest.raises(RuntimeError):
        report_service.get_report("job-123", "json")
