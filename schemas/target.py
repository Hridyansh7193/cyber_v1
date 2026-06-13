from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TargetState(BaseModel):
    domain: str
    scope: List[str] = Field(default_factory=list)
    session_id: str
    start_time: datetime
