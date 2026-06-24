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

class BugHunterConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    settings: SettingsConfig
    llm: LLMConfig
    tools: ToolsConfig
    timeouts: TimeoutsConfig
    reporting: ReportingConfig
