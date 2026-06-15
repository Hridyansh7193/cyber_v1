from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float = Field(ge=0.0)
    raw_output_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
