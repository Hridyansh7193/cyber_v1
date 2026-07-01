from pydantic import BaseModel, ConfigDict
from typing import Any

# Use Any for now to avoid circular dependencies if schemas import this
class RuntimeContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tool_manager: Any
    wordlist_manager: Any
    target_resolver: Any
