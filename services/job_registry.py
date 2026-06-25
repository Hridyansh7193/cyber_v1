from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import datetime, timezone
import uuid

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobState:
    job_id: str
    target_domain: str
    status: JobStatus
    progress: float
    current_stage: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class JobRegistry:
    def __init__(self):
        self._jobs: Dict[str, JobState] = {}

    def create_job(self, target_domain: str, metadata: dict = None) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = JobState(
            job_id=job_id,
            target_domain=target_domain,
            status=JobStatus.PENDING,
            progress=0.0,
            current_stage="init",
            started_at=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        return job_id
        
    def get_job(self, job_id: str) -> Optional[JobState]:
        return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: JobStatus, error: str = None):
        if job_id in self._jobs:
            self._jobs[job_id].status = status
            if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                self._jobs[job_id].completed_at = datetime.now(timezone.utc)
            if error:
                self._jobs[job_id].error = error
                
    def update_progress(self, job_id: str, current_stage: str, progress: float):
        if job_id in self._jobs:
            self._jobs[job_id].current_stage = current_stage
            self._jobs[job_id].progress = progress

    def get_all_jobs(self) -> list[JobState]:
        return list(self._jobs.values())
