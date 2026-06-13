from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ToolResult(BaseModel):
    success: bool
    tool_name: str
    execution_time: float = Field(ge=0.0)
    raw_output_path: Optional[str] = None
    structured_output: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
