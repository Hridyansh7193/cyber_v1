from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Tuple

class TargetState(BaseModel):
    model_config = ConfigDict(frozen=True)
    domain: str
    scope: Tuple[str, ...] = Field(default=())
    out_of_scope: Tuple[str, ...] = Field(default=())
    session_id: str
    start_time: datetime
    
    # New Phase 17 fields
    hostname: str | None = None
    resolved_url: str | None = None
    scheme: str | None = None
    port: int | None = None
    alive: bool = False
    redirect_chain: Tuple[str, ...] = Field(default=())
