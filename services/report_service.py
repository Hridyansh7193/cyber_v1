from typing import List
from reporting.markdown_renderer import generate_markdown
from reporting.json_renderer import generate_json
from schemas.generated_report import GeneratedReport
from schemas.report import Report, ReportFormat

class ReportService:
    """Renders reports into various formats."""
    
    def render_reports(self, reports: List[Report]) -> List[GeneratedReport]:
        rendered = []
        for report in reports:
            if report.report_format == ReportFormat.MARKDOWN:
                rendered.append(generate_markdown(report))
            else:
                rendered.append(generate_json(report))
        return rendered
