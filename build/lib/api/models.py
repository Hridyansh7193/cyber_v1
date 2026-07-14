from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ScanRequest(BaseModel):
    domain: str
    config: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    job_id: str
    message: str

class StatusResponse(BaseModel):
    job_id: str
    target: str
    status: str
    progress: float
    current_stage: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class CancelResponse(BaseModel):
    job_id: str
    cancelled: bool
    message: str
