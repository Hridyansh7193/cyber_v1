from pydantic import BaseModel, Field
from typing import List, Dict, Any

from .target import TargetState
from .task import Task
from .finding import Finding
from .report import Report

class ReconState(BaseModel):
    subdomains: List[str] = Field(default_factory=list)
    alive_hosts: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    parameters: List[str] = Field(default_factory=list)

class JSState(BaseModel):
    js_files: List[str] = Field(default_factory=list)
    endpoints: List[str] = Field(default_factory=list)
    secrets: List[str] = Field(default_factory=list)

class APIState(BaseModel):
    swagger_urls: List[str] = Field(default_factory=list)
    graphql_urls: List[str] = Field(default_factory=list)

class VulnerabilityState(BaseModel):
    nuclei_results: List[Dict[str, Any]] = Field(default_factory=list)
    dalfox_results: List[Dict[str, Any]] = Field(default_factory=list)
    takeovers: List[Dict[str, Any]] = Field(default_factory=list)

class ExecutionState(BaseModel):
    target: TargetState
    task_queue: List[Task] = Field(default_factory=list)
    recon_state: ReconState = Field(default_factory=ReconState)
    js_state: JSState = Field(default_factory=JSState)
    api_state: APIState = Field(default_factory=APIState)
    vuln_state: VulnerabilityState = Field(default_factory=VulnerabilityState)
    findings: List[Finding] = Field(default_factory=list)
    reports: List[Report] = Field(default_factory=list)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
