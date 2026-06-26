from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple, Optional, Any, Mapping
from types import MappingProxyType

from .telemetry import OperationalTelemetry
from .scan_quality import ScanQuality
from .tool_metrics import ToolMetrics

class OperationalState(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    version: int = Field(default=1)
    telemetry: Optional[OperationalTelemetry] = Field(default=None)
    scan_quality: Optional[ScanQuality] = Field(default=None)
    tool_metrics: Tuple[ToolMetrics, ...] = Field(default=())
    benchmark_metrics: Mapping[str, Any] = Field(default_factory=lambda: MappingProxyType({}))
