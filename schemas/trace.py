from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class TraceEvent(BaseModel):
    stage: str
    plugin: str
    received: int
    stdout_lines: int
    parsed: int
    stored: int
    runtime: float
    success: bool
    exit_code: int
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    workspace_file: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TraceReport(BaseModel):
    job_id: str
    target: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime = Field(default_factory=datetime.utcnow)
    planner_profile: str = "default"
    bughunter_version: str = "1.0.0"
    trace: List[TraceEvent] = Field(default_factory=list)
