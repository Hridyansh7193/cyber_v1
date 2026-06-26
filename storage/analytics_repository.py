import sqlite3
import json
from typing import List, Optional
from schemas.tool_metrics import ToolMetrics
from contextlib import contextmanager
import os

class AnalyticsRepository:
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tool_name TEXT NOT NULL,
                    version TEXT,
                    runtime REAL,
                    exit_code INTEGER,
                    timeout BOOLEAN,
                    stdout_size INTEGER,
                    stderr_size INTEGER,
                    parsed_objects INTEGER,
                    parser_errors INTEGER,
                    wrapper_errors INTEGER,
                    memory REAL,
                    success BOOLEAN
                )
            """)

    def insert_metric(self, metric: ToolMetrics) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tool_metrics (
                    tool_name, version, runtime, exit_code, timeout,
                    stdout_size, stderr_size, parsed_objects, parser_errors,
                    wrapper_errors, memory, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.tool_name,
                metric.version,
                metric.runtime,
                metric.exit_code,
                metric.timeout,
                metric.stdout_size,
                metric.stderr_size,
                metric.parsed_objects,
                metric.parser_errors,
                metric.wrapper_errors,
                metric.memory,
                metric.success
            ))

    def get_tool_history(self, tool_name: str, limit: int = 100) -> List[ToolMetrics]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tool_metrics 
                WHERE tool_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (tool_name, limit))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(ToolMetrics(
                    tool_name=row["tool_name"],
                    version=row["version"],
                    runtime=row["runtime"],
                    exit_code=row["exit_code"],
                    timeout=bool(row["timeout"]),
                    stdout_size=row["stdout_size"],
                    stderr_size=row["stderr_size"],
                    parsed_objects=row["parsed_objects"],
                    parser_errors=row["parser_errors"],
                    wrapper_errors=row["wrapper_errors"],
                    memory=row["memory"],
                    success=bool(row["success"])
                ))
            return results

    def get_health_stats(self) -> dict:
        """Returns aggregate success rates for tools."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tool_name, 
                       COUNT(*) as total_runs, 
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
                       AVG(runtime) as avg_runtime
                FROM tool_metrics
                GROUP BY tool_name
            """)
            
            rows = cursor.fetchall()
            stats = {}
            for row in rows:
                total = row["total_runs"]
                successes = row["successful_runs"]
                stats[row["tool_name"]] = {
                    "total_runs": total,
                    "success_rate": (successes / total * 100) if total > 0 else 0.0,
                    "avg_runtime": row["avg_runtime"]
                }
            return stats

    def clear(self) -> None:
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
