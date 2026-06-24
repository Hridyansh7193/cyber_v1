from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Tuple

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"

class Finding(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    severity: Severity
    confidence: Confidence
    evidence: str
    references: Tuple[str, ...] = Field(default=())
