from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, UTC
from enum import Enum
from typing import Tuple, Optional
from uuid import UUID, uuid4
from .finding import Finding
from .intelligence import IntelligenceState

class ReportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"

class Report(BaseModel):
    model_config = ConfigDict(frozen=True)
    report_id: UUID = Field(default_factory=uuid4)
    session_id: str = "default"
    report_path: str = ""
    report_format: ReportFormat = ReportFormat.MARKDOWN
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    findings: Tuple[Finding, ...] = Field(default=())
    total_findings: int = 0
    intelligence: Optional[IntelligenceState] = Field(default=None)
