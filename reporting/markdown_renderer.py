import importlib.resources
from jinja2 import Environment
from schemas.report import Report
from schemas.generated_report import GeneratedReport

_ENV = Environment(autoescape=False)
_TEMPLATE = None

def generate_markdown(report: Report) -> GeneratedReport:
    global _TEMPLATE
    if _TEMPLATE is None:
        template_str = importlib.resources.files("reporting.templates").joinpath("report.md.j2").read_text(encoding="utf-8")
        _TEMPLATE = _ENV.from_string(template_str)
        
    # generate the single string natively
    content = _TEMPLATE.render(report=report)
    
    return GeneratedReport(
        report_id=report.report_id,
        format="markdown",
        filename=f"report_{report.report_id}.md",
        mime_type="text/markdown",
        encoding="utf-8",
        content=content,
        is_binary=False
    )
