from pydantic import BaseModel, ConfigDict, Field

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
