from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple, Dict, Any

from schemas.report import Report
from schemas.finding import Finding
from schemas.task import Task

class TaskQueueDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    task_queue: Tuple[Task, ...]

class ReconDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    subdomains: Tuple[str, ...]
    alive_hosts: Tuple[str, ...]
    urls: Tuple[str, ...]
    tech_stack: Dict[str, Tuple[str, ...]] = Field(default_factory=dict)
    waf_detected: Dict[str, bool] = Field(default_factory=dict)

class JSDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    js_files: Tuple[str, ...]
    endpoints: Tuple[str, ...]

class APIDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    swagger_urls: Tuple[str, ...]
    graphql_urls: Tuple[str, ...]

class VulnerabilityDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    findings: Tuple[Dict[str, Any], ...]

class FindingDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    findings: Tuple[Finding, ...]

class ReportDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    reports: Tuple[Report, ...]

from .intelligence_delta import IntelligenceDelta
