import csv
import io
from schemas.report import Report
from schemas.generated_report import GeneratedReport

def generate_csv(report: Report) -> GeneratedReport:
    """Generates a CSV report from a Report object."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["ID", "Title", "Severity", "Confidence", "Source Tool", "Evidence"])
    
    # Write findings
    for finding in report.findings:
        writer.writerow([
            finding.id,
            finding.title,
            finding.severity,
            finding.confidence,
            finding.source_tool,
            finding.evidence
        ])
        
    content = output.getvalue()
    
    filename = "report.csv"
    if report.report_path:
        from pathlib import Path
        filename = Path(report.report_path).name.replace(".json", ".csv").replace(".md", ".csv")
        
    return GeneratedReport(
        report_id=report.report_id,
        format="csv",
        filename=filename,
        mime_type="text/csv",
        content=content
    )
