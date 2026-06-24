from .target import TargetState
from .task import Task, TaskPriority, TaskStatus
from .finding import Finding, Severity, Confidence
from .report import Report, ReportFormat
from .tool_result import ToolResult

import copyreg
from types import MappingProxyType

def _pickle_mappingproxy(proxy):
    return MappingProxyType, (dict(proxy),)

copyreg.pickle(MappingProxyType, _pickle_mappingproxy)
from .state import ReconState, JSState, APIState, VulnerabilityState, ExecutionState
from .generated_report import GeneratedReport
