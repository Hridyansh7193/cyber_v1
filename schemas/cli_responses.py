from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AnalyticsResponse(BaseModel):
    total_scans: int
    successful_scans: int
    failed_scans: int
    average_runtime: float
    median_runtime: float
    fastest_runtime: float
    slowest_runtime: float
    average_findings: float
    severity_distribution: Dict[str, int]
    plugin_runtime_avg: Dict[str, float]
    planner_runtime_avg: float
    most_used_plugins: List[str]
    most_active_targets: List[str]
    reports_generated: int
    workspace_usage_bytes: int
    scans_per_day: Dict[str, int]
    findings_per_day: Dict[str, int]
    reports_per_day: Dict[str, int]
    runtime_trend: List[float]
    success_rate_trend: List[float]

class SearchResponse(BaseModel):
    query: str
    entity_type: str
    total_matches: int
    results: List[Dict[str, Any]]

class PlannerResponse(BaseModel):
    planner_version: str
    confidence: float
    executed_nodes: List[str]
    skipped_nodes: List[str]
    reasoning: str
    execution_plan: Dict[str, Any]
    overrides: List[str]

class CleanupResponse(BaseModel):
    cache_files: int
    cache_size_bytes: int
    temp_files: int
    temp_size_bytes: int
    logs_deleted: int
    workspace_removed: int
    elapsed_time_seconds: float
    is_dry_run: bool

class StatusResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
