from pydantic import BaseModel, ConfigDict
from typing import Literal, Union
from uuid import UUID

class GeneratedReport(BaseModel):
    report_id: UUID
    format: Literal["markdown", "json"]
    filename: str
    mime_type: str
    encoding: str = "utf-8"
    content: Union[str, bytes]
    is_binary: bool = False

    model_config = ConfigDict(frozen=True)
