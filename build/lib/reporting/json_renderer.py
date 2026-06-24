import json
from schemas.report import Report
from schemas.generated_report import GeneratedReport

def generate_json(report: Report) -> GeneratedReport:
    # Serialize the report using Pydantic's JSON dumper
    data = report.model_dump(mode="json")
    content = json.dumps(data, indent=2, ensure_ascii=False)
    
    return GeneratedReport(
        report_id=report.report_id,
        format="json",
        filename=f"report_{report.report_id}.json",
        mime_type="application/json",
        encoding="utf-8",
        content=content,
        is_binary=False
    )
