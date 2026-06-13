from pydantic import BaseModel, Field
from enum import Enum
from typing import List

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
    title: str
    severity: Severity
    confidence: Confidence
    evidence: str
    references: List[str] = Field(default_factory=list)
