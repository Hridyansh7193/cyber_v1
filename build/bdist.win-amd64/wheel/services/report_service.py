from typing import List
from reporting.markdown_renderer import generate_markdown
from reporting.json_renderer import generate_json
from reporting.sarif_renderer import generate_sarif
from reporting.csv_renderer import generate_csv
from reporting.burpxml_renderer import generate_burpxml
from schemas.generated_report import GeneratedReport
from schemas.report import Report, ReportFormat

class ReportService:
    """Renders reports into various formats."""
    
    def render_reports(self, reports: List[Report]) -> List[GeneratedReport]:
        rendered = []
        for report in reports:
            if report.report_format == ReportFormat.MARKDOWN:
                rendered.append(generate_markdown(report))
            elif report.report_format == ReportFormat.JSON:
                rendered.append(generate_json(report))
            elif report.report_format == ReportFormat.SARIF:
                rendered.append(generate_sarif(report))
            elif report.report_format == ReportFormat.CSV:
                rendered.append(generate_csv(report))
            elif report.report_format == ReportFormat.BURP_XML:
                rendered.append(generate_burpxml(report))
        return rendered
