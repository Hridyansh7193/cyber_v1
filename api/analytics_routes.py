from fastapi import APIRouter, Depends
from api.dependencies import get_analytics_service
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/health")
def get_health(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_health_stats()

@router.get("/tools")
def list_tools(service: AnalyticsService = Depends(get_analytics_service)):
    stats = service.get_health_stats()
    return {"tools": list(stats.keys())}

@router.get("/history/{tool_name}")
def get_history(tool_name: str, limit: int = 100, service: AnalyticsService = Depends(get_analytics_service)):
    history = service.get_tool_history(tool_name, limit)
    return {"tool": tool_name, "history": history}
