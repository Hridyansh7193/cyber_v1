from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, UTC
from enum import Enum
from typing import Tuple, Optional
from uuid import UUID, uuid4
from .finding import Finding
from .intelligence import IntelligenceState
from .operational import OperationalState

from .telemetry import ExecutionTelemetry

class ReportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"

class DiscoveredAssets(BaseModel):
    model_config = ConfigDict(frozen=True)
    subdomains: Tuple[str, ...] = Field(default=())
    hosts: Tuple[str, ...] = Field(default=())
    urls: Tuple[str, ...] = Field(default=())
    javascript: Tuple[str, ...] = Field(default=())
    apis: Tuple[str, ...] = Field(default=())
    secrets: Tuple[str, ...] = Field(default=())
    swagger_endpoints: Tuple[str, ...] = Field(default=())
    graphql_endpoints: Tuple[str, ...] = Field(default=())
    technologies: Tuple[str, ...] = Field(default=())
    response_titles: Tuple[str, ...] = Field(default=())
    status_codes: Tuple[str, ...] = Field(default=())
    takeovers: Tuple[str, ...] = Field(default=())
    fuzz_results: Tuple[str, ...] = Field(default=())

class RuntimeMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    bughunter_version: str = "1.0.0"
    schema_version: str = "v2"
    plugin_versions: dict[str, str] = Field(default_factory=dict)
    config_version: str = "v2"
    profile: str = "default"
    db_version: str = "v1"
    git_commit: str = "latest"
    build_date: str = ""
    os: str = ""
    python_version: str = ""
    go_version: str = ""

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
    assets: DiscoveredAssets = Field(default_factory=DiscoveredAssets)
    telemetry: Tuple[ExecutionTelemetry, ...] = Field(default=())
    intelligence: Optional[IntelligenceState] = Field(default=None)
    operational: Optional[OperationalState] = Field(default=None)
    runtime_metadata: Optional[RuntimeMetadata] = Field(default=None)
    tool_versions: dict[str, str] = Field(default_factory=dict)
    tool_paths: dict[str, str] = Field(default_factory=dict)
    skipped_plugins: Tuple[str, ...] = Field(default=())
    failed_plugins: Tuple[str, ...] = Field(default=())
    retry_counts: dict[str, int] = Field(default_factory=dict)
    execution_timeline: Tuple[dict, ...] = Field(default=())
    plugin_statistics: dict[str, dict] = Field(default_factory=dict)
