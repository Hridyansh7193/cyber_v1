from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Tuple

class ExecutionTelemetry(BaseModel):
    model_config = ConfigDict(frozen=True)
    tool: str
    version: str
    command: Optional[str] = None
    execution_time: float
    exit_code: int
    stdout_size: int
    stderr_size: int
    parsed_objects: int
    success: bool
    timeout: bool = False
    wrapper_errors: Tuple[str, ...] = Field(default_factory=tuple)
    parser_errors: Tuple[str, ...] = Field(default_factory=tuple)
    binary_path: Optional[str] = None
    working_directory: Optional[str] = None
class OperationalTelemetry(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    scan_duration: float = Field(default=0.0)
    planner_duration: float = Field(default=0.0)
    analysis_duration: float = Field(default=0.0)
    report_duration: float = Field(default=0.0)
    checkpoint_duration: float = Field(default=0.0)
    
    checkpoint_count: int = Field(default=0)
    subdomains: int = Field(default=0)
    hosts: int = Field(default=0)
    urls: int = Field(default=0)
    js_files: int = Field(default=0)
    apis: int = Field(default=0)
    parameters: int = Field(default=0)
    findings: int = Field(default=0)
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    
    peak_rss: float = Field(default=0.0)
    cpu_time: float = Field(default=0.0)
    report_size: int = Field(default=0)
    checkpoint_size: int = Field(default=0)
