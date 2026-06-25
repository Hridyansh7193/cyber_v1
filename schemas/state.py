from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Tuple, Mapping, Any, Optional
from types import MappingProxyType

from .target import TargetState
from .task import Task
from .finding import Finding
from .report import Report
from .intelligence import IntelligenceState

class ReconState(BaseModel):
    model_config = ConfigDict(frozen=True)
    subdomains: Tuple[str, ...] = Field(default=())
    alive_hosts: Tuple[str, ...] = Field(default=())
    urls: Tuple[str, ...] = Field(default=())
    parameters: Tuple[str, ...] = Field(default=())

class JSState(BaseModel):
    model_config = ConfigDict(frozen=True)
    js_files: Tuple[str, ...] = Field(default=())
    endpoints: Tuple[str, ...] = Field(default=())
    secrets: Tuple[str, ...] = Field(default=())

class APIState(BaseModel):
    model_config = ConfigDict(frozen=True)
    swagger_urls: Tuple[str, ...] = Field(default=())
    graphql_urls: Tuple[str, ...] = Field(default=())

class VulnerabilityState(BaseModel):
    model_config = ConfigDict(frozen=True)
    nuclei_results: Tuple[Mapping[str, Any], ...] = Field(default=())
    dalfox_results: Tuple[Mapping[str, Any], ...] = Field(default=())
    takeovers: Tuple[Mapping[str, Any], ...] = Field(default=())

class ExecutionState(BaseModel):
    model_config = ConfigDict(frozen=True)
    target: TargetState
    task_queue: Tuple[Task, ...] = Field(default=())
    recon_state: ReconState = Field(default_factory=ReconState)
    js_state: JSState = Field(default_factory=JSState)
    api_state: APIState = Field(default_factory=APIState)
    vuln_state: VulnerabilityState = Field(default_factory=VulnerabilityState)
    findings: Tuple[Finding, ...] = Field(default=())
    reports: Tuple[Report, ...] = Field(default=())
    logs: Tuple[Mapping[str, Any], ...] = Field(default=())
    metadata: Mapping[str, Any] = Field(default_factory=lambda: MappingProxyType({}))
    intelligence: Optional[IntelligenceState] = Field(default=None)

    @field_serializer('metadata')
    def serialize_metadata(self, v: Mapping[str, Any], _info):
        return dict(v)
