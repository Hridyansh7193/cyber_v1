from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import Enum
from typing import Tuple
import hashlib

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
    id: str = Field(default="")
    title: str
    severity: Severity
    confidence: Confidence
    evidence: str
    poc: str = Field(default="")
    source_tool: str = Field(default="unknown")
    references: Tuple[str, ...] = Field(default=())
    
    @model_validator(mode='before')
    @classmethod
    def generate_id(cls, data: dict) -> dict:
        if not data.get('id'):
            title = data.get('title', '')
            evidence = data.get('evidence', '')
            hasher = hashlib.sha256(f"{title}:{evidence}".encode('utf-8'))
            data['id'] = hasher.hexdigest()[:16]
        return data
