from typing import Dict, Optional
from services.orchestrator_adapter import OrchestratorAdapter
from reporting.markdown_renderer import generate_markdown
from reporting.json_renderer import generate_json
from schemas.generated_report import GeneratedReport
from schemas.report import ReportFormat

class ReportService:
    """Loads and renders reports."""
    
    def __init__(self, adapter: OrchestratorAdapter):
        self._adapter = adapter

    def get_report(self, job_id: str, format_type: str = "json") -> Optional[GeneratedReport]:
        reports = self._adapter.get_report(job_id)
        if not reports:
            return None
            
        # Find the requested format
        target_report = None
        for report in reports:
            if report.report_format.value == format_type.lower():
                target_report = report
                break
                
        if not target_report:
            return None
            
        if target_report.report_format == ReportFormat.MARKDOWN:
            return generate_markdown(target_report)
        else:
            return generate_json(target_report)
