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
    plugin: str = Field(default="unknown")
    tool_version: str = Field(default="unknown")
    target: str = Field(default="unknown")
    url: str = Field(default="unknown")
    template_id: str = Field(default="unknown")
    category: str = Field(default="unknown")
    tags: Tuple[str, ...] = Field(default=())
    recommendation: str = Field(default="")
    timestamp: str = Field(default="")
    command: str = Field(default="")
    replay_command: str = Field(default="")
    parser: str = Field(default="unknown")
    metadata: dict[str, str] = Field(default_factory=dict)
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
