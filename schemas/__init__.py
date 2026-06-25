from .target import TargetState
from .task import Task, TaskPriority, TaskStatus
from .finding import Finding, Severity, Confidence
from .report import Report, ReportFormat
from .tool_result import ToolResult
from .planner_decision import PlannerDecision
from .prioritized_asset import PrioritizedAsset
from .correlated_finding import CorrelatedFinding
from .attack_graph import AttackGraph, AttackGraphNode, AttackGraphEdge
from .risk_summary import RiskSummary
from .intelligence import IntelligenceState

import copyreg
from types import MappingProxyType

def _pickle_mappingproxy(proxy):
    return MappingProxyType, (dict(proxy),)

copyreg.pickle(MappingProxyType, _pickle_mappingproxy)
from .state import ReconState, JSState, APIState, VulnerabilityState, ExecutionState
from .generated_report import GeneratedReport
