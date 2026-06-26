import os
import pytest
from storage.analytics_repository import AnalyticsRepository
from schemas.tool_metrics import ToolMetrics

@pytest.fixture
def repo():
    test_db = "test_analytics.db"
    repo = AnalyticsRepository(db_path=test_db)
    yield repo
    if os.path.exists(test_db):
        os.remove(test_db)

def test_analytics_repository_insert_and_retrieve(repo):
    metric = ToolMetrics(
        tool_name="subfinder",
        version="2.6.6",
        runtime=1.5,
        exit_code=0,
        timeout=False,
        stdout_size=1024,
        stderr_size=0,
        parsed_objects=10,
        parser_errors=0,
        wrapper_errors=0,
        memory=50.0,
        success=True
    )
    
    repo.insert_metric(metric)
    
    history = repo.get_tool_history("subfinder")
    assert len(history) == 1
    
    retrieved = history[0]
    assert retrieved.tool_name == "subfinder"
    assert retrieved.runtime == 1.5
    assert retrieved.success is True
    assert retrieved.parsed_objects == 10

def test_analytics_health_stats(repo):
    # Insert 3 successes and 1 failure for subfinder
    for _ in range(3):
        repo.insert_metric(ToolMetrics(tool_name="subfinder", runtime=1.0, success=True))
    repo.insert_metric(ToolMetrics(tool_name="subfinder", runtime=2.0, success=False))
    
    # Insert 1 success for httpx
    repo.insert_metric(ToolMetrics(tool_name="httpx", runtime=0.5, success=True))
    
    stats = repo.get_health_stats()
    
    assert "subfinder" in stats
    assert stats["subfinder"]["total_runs"] == 4
    assert stats["subfinder"]["success_rate"] == 75.0
    assert stats["subfinder"]["avg_runtime"] == 1.25  # (1+1+1+2)/4
    
    assert "httpx" in stats
    assert stats["httpx"]["total_runs"] == 1
    assert stats["httpx"]["success_rate"] == 100.0
