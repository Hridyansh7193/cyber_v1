from pydantic import BaseModel, ConfigDict
from typing import Literal, List, Optional
from enum import Enum

class Capability(str, Enum):
    RECON = "Recon"
    PASSIVE_RECON = "PassiveRecon"
    DNS = "DNS"
    HTTP = "HTTP"
    JS = "JS"
    API = "API"
    SECRETS = "Secrets"
    FUZZING = "Fuzzing"
    VULN = "Vuln"
    PARAMETER_DISCOVERY = "ParameterDiscovery"
    REPORTING = "Reporting"
    ANALYTICS = "Analytics"

class SelfTestResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    binary: bool
    execution: bool
    parser: bool
    metadata_builder: bool
    candidate_routing: bool

    @property
    def passed(self) -> bool:
        return self.binary and self.execution and self.parser and self.metadata_builder and self.candidate_routing

class RuntimeCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    status: Literal["PASS", "WARNING", "FAIL"]
    message: str
    remediation: Optional[str] = None

class DependencyStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool: str
    version: Optional[str]
    installed: bool
    status: Literal["PASS", "WARNING", "FAIL"]
    message: str

class PluginStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    plugin: str
    capabilities: List[Capability]
    version: Optional[str]
    status: Literal["PASS", "WARNING", "FAIL"]
    message: str

class EnvironmentStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    os: str
    kernel: str
    python_version: str
    go_version: Optional[str]
    cpu_cores: int
    memory_gb: float
    docker_available: bool

class InstallationStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    installed: bool
    version: str
    path: str
    plugins_installed: int
    templates_installed: bool

class SystemBenchmark(BaseModel):
    model_config = ConfigDict(frozen=True)

    cpu_usage_percent: float
    ram_usage_percent: float
    open_file_limit: int
    sqlite_write_ms: float

class RuntimeReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: EnvironmentStatus
    dependencies: List[DependencyStatus]
    plugins: List[PluginStatus]
    benchmark: SystemBenchmark
    checks: List[RuntimeCheck]
    summary_pass: int
    summary_warn: int
    summary_fail: int

class InstallPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    steps: List[str]
    dry_run: bool

class InstallStep(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    description: str

class InstallResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    step: str
    success: bool
    output: str

class InstallSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    results: List[InstallResult]
    total_time_ms: float
