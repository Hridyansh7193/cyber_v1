from typing import Dict, Any, List
from storage.analytics_repository import AnalyticsRepository
from schemas.tool_metrics import ToolMetrics

class AnalyticsService:
    def __init__(self):
        self._repo = AnalyticsRepository("analytics.db")
        
    def get_health_stats(self) -> Dict[str, Any]:
        return self._repo.get_health_stats()
        
    def get_tool_history(self, tool_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._repo.get_tool_history(tool_name, limit)
