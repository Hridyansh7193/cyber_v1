from schemas.report import Report
from schemas.generated_report import GeneratedReport

def generate_json(report: Report) -> GeneratedReport:
    # Serialize the report using Pydantic's JSON dumper incrementally
    content = report.model_dump_json(indent=2)
    
    return GeneratedReport(
        report_id=report.report_id,
        format="json",
        filename=f"report_{report.report_id}.json",
        mime_type="application/json",
        encoding="utf-8",
        content=content,
        is_binary=False
    )
