import json
from schemas.report import Report
from schemas.generated_report import GeneratedReport

def generate_sarif(report: Report) -> GeneratedReport:
    """Generates a SARIF report from a Report object."""
    
    results = []
    for finding in report.findings:
        results.append({
            "ruleId": finding.id,
            "message": {
                "text": finding.title
            },
            "level": "error" if finding.severity.lower() in ["high", "critical"] else ("warning" if finding.severity.lower() == "medium" else "note"),
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.evidence[:200]
                        }
                    }
                }
            ]
        })

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "BugHunter",
                        "informationUri": "https://github.com/bughunter/bughunter",
                        "version": report.runtime_metadata.bughunter_version if report.runtime_metadata else "1.0.0"
                    }
                },
                "results": results
            }
        ]
    }
    
    filename = "report.sarif"
    if report.report_path:
        from pathlib import Path
        filename = Path(report.report_path).name.replace(".json", ".sarif").replace(".md", ".sarif")

    return GeneratedReport(
        report_id=report.report_id,
        format="sarif",
        filename=filename,
        mime_type="application/sarif+json",
        content=json.dumps(sarif, indent=2)
    )
