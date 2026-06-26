from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from storage.analytics_repository import AnalyticsRepository
from schemas.tool_metrics import ToolMetrics
from api.dependencies import get_scan_service

# Note: Ideally AnalyticsRepository should be injected via Depends.
# For simplicity, we create a global or depend on a singleton.
# We'll write a small dependency wrapper here.

def get_analytics_repository() -> AnalyticsRepository:
    # Use a default db
    return AnalyticsRepository("analytics.db")

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/health")
def get_health(repo: AnalyticsRepository = Depends(get_analytics_repository)):
    return repo.get_health_stats()

@router.get("/tools")
def list_tools(repo: AnalyticsRepository = Depends(get_analytics_repository)):
    stats = repo.get_health_stats()
    return {"tools": list(stats.keys())}

@router.get("/history/{tool_name}")
def get_history(tool_name: str, limit: int = 100, repo: AnalyticsRepository = Depends(get_analytics_repository)):
    history = repo.get_tool_history(tool_name, limit)
    return {"tool": tool_name, "history": history}
