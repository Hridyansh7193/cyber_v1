from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional

class SettingsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    scan_depth: int
    max_concurrency: int
    log_level: str

class LLMConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    provider: str
    default_model: str
    timeout: int
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

class ToolsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    tool_paths: Dict[str, str]
    docker_container_names: Dict[str, str]
    wordlists: Dict[str, str]
    enable_flags: Dict[str, bool]

class TimeoutsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    subfinder_timeout: int
    nuclei_timeout: int
    dalfox_timeout: int
    ffuf_timeout: int
    global_timeout: int

class ReportingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    report_formats: List[str]
    output_directories: Dict[str, str]

class ResourceLimitsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_memory_mb: int = 4096
    max_runtime_seconds: int = 3600
    max_threads: int = 100
    max_subdomains: int = 10000
    max_urls: int = 50000
    max_findings: int = 1000

from enum import Enum

class PerformanceProfile(str, Enum):
    LIGHT = "light"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class ExecutionBudget(BaseModel):
    model_config = ConfigDict(frozen=True)
    max_runtime_seconds: int = 3600
    max_targets_per_plugin: int = 5000
    max_retries: int = 3
    max_failures: int = 100

class AuthConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    headers: List[str] = []

class BugHunterConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: str = "2"
    settings: SettingsConfig
    llm: LLMConfig
    tools: ToolsConfig
    timeouts: TimeoutsConfig
    reporting: ReportingConfig
    resource_limits: ResourceLimitsConfig = ResourceLimitsConfig()
    auth: AuthConfig = AuthConfig()
    execution_budget: ExecutionBudget = ExecutionBudget()
    profile: PerformanceProfile = PerformanceProfile.BALANCED
