import os
from jinja2 import Environment, select_autoescape
from schemas.report import Report
from schemas.generated_report import GeneratedReport

_ENV = Environment(autoescape=select_autoescape(default_for_string=False, default=False))
_TEMPLATE = None

def generate_markdown(report: Report) -> GeneratedReport:
    global _TEMPLATE
    if _TEMPLATE is None:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "report.md.j2")
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        _TEMPLATE = _ENV.from_string(template_str)
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
