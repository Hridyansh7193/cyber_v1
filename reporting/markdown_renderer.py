import importlib.resources
from jinja2 import Environment
from schemas.report import Report
from schemas.generated_report import GeneratedReport

def generate_markdown(report: Report) -> GeneratedReport:
    # Python 3.9+
    template_str = importlib.resources.files("reporting.templates").joinpath("report.md.j2").read_text(encoding="utf-8")
    
    env = Environment(autoescape=False)
    template = env.from_string(template_str)
    
    content = template.render(report=report)
    
    return GeneratedReport(
        report_id=report.report_id,
        format="markdown",
        filename=f"report_{report.report_id}.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content=content,
        is_binary=False
    )
