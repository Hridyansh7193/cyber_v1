from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from enum import Enum
from typing import Tuple
from uuid import UUID
from .finding import Finding

class ReportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"

class Report(BaseModel):
    model_config = ConfigDict(frozen=True)
    report_id: UUID
    session_id: str = "default"
    report_path: str = ""
    report_format: ReportFormat = ReportFormat.MARKDOWN
    created_at: datetime
    timestamp: datetime = Field(default_factory=datetime.utcnow) # Kept for backwards compatibility
    findings: Tuple[Finding, ...] = Field(default=())
    total_findings: int = 0
