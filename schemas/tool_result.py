from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, Any, Tuple, Mapping
from types import MappingProxyType

class ToolResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    tool_name: str
    plugin_version: str = "unknown"
    binary_path: Optional[str] = None
    command: Optional[str] = None
    working_directory: Optional[str] = None
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    stdout_size: int = 0
    parsed_findings: int = 0
    received_count: int = 1
    errors: Tuple[str, ...] = Field(default_factory=tuple)
    error_message: Optional[str] = None
    execution_time: float = Field(ge=0.0)
    raw_output_path: Optional[str] = None
    parsed_output: Tuple[Any, ...] = Field(default_factory=tuple)
    metadata_schema_version: int = 1
    metadata: Mapping[str, Any] = Field(default_factory=lambda: MappingProxyType({}))

    @field_serializer('metadata')
    def serialize_metadata(self, v: Mapping[str, Any], _info):
        return dict(v)
