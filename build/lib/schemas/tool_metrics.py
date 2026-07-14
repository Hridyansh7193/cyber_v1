from pydantic import BaseModel, ConfigDict, Field

class ToolMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    tool_name: str
    version: str = Field(default="unknown")
    runtime: float = Field(default=0.0)
    exit_code: int = Field(default=0)
    timeout: bool = Field(default=False)
    stdout_size: int = Field(default=0)
    stderr_size: int = Field(default=0)
    parsed_objects: int = Field(default=0)
    parser_errors: int = Field(default=0)
    wrapper_errors: int = Field(default=0)
    memory: float = Field(default=0.0)
    success: bool = Field(default=False)
