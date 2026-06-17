from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class ReportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"

class Report(BaseModel):
    model_config = ConfigDict(frozen=True)
    session_id: str
    report_path: str
    report_format: ReportFormat
    timestamp: datetime
