from pydantic import BaseModel, ConfigDict, Field
from typing import Any
from schemas.trace import TraceReport

# Use Any for now to avoid circular dependencies if schemas import this
class RuntimeContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tool_manager: Any
    wordlist_manager: Any
    target_resolver: Any
    
    # Execution tracing
    trace: TraceReport = Field(default_factory=lambda: TraceReport(job_id="unknown", target="unknown"))
