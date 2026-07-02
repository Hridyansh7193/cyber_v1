from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple, Dict, Any

from schemas.report import Report
from schemas.finding import Finding

class PlannerDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    recommended_actions: Tuple[str, ...]

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

class AnalysisDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    grouped_findings: Tuple[Dict[str, Any], ...]

class ReportDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    reports: Tuple[Report, ...]

from .intelligence_delta import IntelligenceDelta
