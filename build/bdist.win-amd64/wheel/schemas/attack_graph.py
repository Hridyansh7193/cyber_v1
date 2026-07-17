from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple

class AttackGraphNode(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: str
    type: str
    label: str

class AttackGraphEdge(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    source: str
    target: str
    relationship: str

class AttackGraph(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    nodes: Tuple[AttackGraphNode, ...] = Field(default=())
    edges: Tuple[AttackGraphEdge, ...] = Field(default=())
    entry_points: Tuple[str, ...] = Field(default=())
    attack_paths: Tuple[str, ...] = Field(default=())
    confidence: float = Field(default=0.0)
