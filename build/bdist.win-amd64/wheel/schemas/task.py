from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Tuple

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = Field(default=0, ge=0)
    dependencies: Tuple[str, ...] = Field(default=())
