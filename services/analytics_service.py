from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime
from services.persistence_service import PersistenceService

class AnalyticsService:
    def __init__(self, persistence_service: PersistenceService):
        self.persistence = persistence_service
        
    def get_tool_history(self, tool_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self.persistence.analytics_repo.get_tool_history(tool_name, limit)

    def get_aggregate_analytics(self) -> Dict[str, Any]:
        sessions = self.persistence.get_all_sessions()
        reports = self.persistence.get_all_reports()
        findings = self.persistence.get_all_findings()
        
        total_scans = len(sessions)
        successful_scans = len([s for s in sessions if s.status == "completed"])
        failed_scans = total_scans - successful_scans
        
        runtimes = []
        for s in sessions:
            if s.finished_at and s.started_at:
                # Convert string datetime if necessary, assuming models provide datetime objects
                end = s.finished_at
                start = s.started_at
                if isinstance(end, str):
                    end = datetime.fromisoformat(end)
                if isinstance(start, str):
                    start = datetime.fromisoformat(start)
                runtimes.append((end - start).total_seconds())
                
        avg_rt = sum(runtimes) / len(runtimes) if runtimes else 0.0
        sorted_rt = sorted(runtimes)
        median_rt = sorted_rt[len(sorted_rt)//2] if sorted_rt else 0.0
        fastest_rt = min(runtimes) if runtimes else 0.0
        slowest_rt = max(runtimes) if runtimes else 0.0
        
        severity_dist = defaultdict(int)
        for f in findings:
            severity_dist[f.severity] += 1
            
        avg_findings = len(findings) / total_scans if total_scans else 0.0
        
        tool_stats = self.persistence.analytics_repo.get_health_stats()
        plugin_runtime_avg = {k: v["avg_runtime"] for k, v in tool_stats.items()}
        
        # Calculate trends
        scans_per_day = defaultdict(int)
        findings_per_day = defaultdict(int)
        reports_per_day = defaultdict(int)
        
        for s in sessions:
            if s.started_at:
                st = s.started_at
                if isinstance(st, str): st = datetime.fromisoformat(st)
                day_str = st.strftime("%Y-%m-%d")
                scans_per_day[day_str] += 1
                
        for f in findings:
            if f.created_at:
                ct = f.created_at
                if isinstance(ct, str): ct = datetime.fromisoformat(ct)
                day_str = ct.strftime("%Y-%m-%d")
                findings_per_day[day_str] += 1
                
        for r in reports:
            if r.created_at:
                ct = r.created_at
                if isinstance(ct, str): ct = datetime.fromisoformat(ct)
                day_str = ct.strftime("%Y-%m-%d")
                reports_per_day[day_str] += 1

        # Most used plugins (by total_runs)
        sorted_tools = sorted(tool_stats.items(), key=lambda x: x[1]["total_runs"], reverse=True)
        most_used_plugins = [t[0] for t in sorted_tools[:5]]
        
        # Target activity
        target_counts = defaultdict(int)
        for s in sessions:
            target_counts[s.target_domain] += 1
        most_active_targets = [k for k, v in sorted(target_counts.items(), key=lambda item: item[1], reverse=True)[:5]]

        return {
            "total_scans": total_scans,
            "successful_scans": successful_scans,
            "failed_scans": failed_scans,
            "average_runtime": avg_rt,
            "median_runtime": median_rt,
            "fastest_runtime": fastest_rt,
            "slowest_runtime": slowest_rt,
            "average_findings": avg_findings,
            "severity_distribution": dict(severity_dist),
            "plugin_runtime_avg": plugin_runtime_avg,
            "planner_runtime_avg": 0.0, # Could be extracted from logs if needed
            "most_used_plugins": most_used_plugins,
            "most_active_targets": most_active_targets,
            "reports_generated": len(reports),
            "workspace_usage_bytes": 0, # Evaluated in workspace command usually
            "scans_per_day": dict(scans_per_day),
            "findings_per_day": dict(findings_per_day),
            "reports_per_day": dict(reports_per_day),
            "runtime_trend": runtimes[-10:], # simple proxy for trend
            "success_rate_trend": []
        }
