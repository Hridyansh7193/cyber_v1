from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Tuple

class TargetState(BaseModel):
    model_config = ConfigDict(frozen=True)
    domain: str
    scope: Tuple[str, ...] = Field(default=())
    session_id: str
    start_time: datetime
