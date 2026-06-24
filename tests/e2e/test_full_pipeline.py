import pytest
from pathlib import Path

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from storage.database import get_db_session
from storage.models import TargetModel, SubdomainModel, UrlModel, FindingModel

def test_full_pipeline_success(e2e_db, mock_subprocess_run, base_config, deterministic_target):
    # Setup graph
    app = build_graph(base_config)
    
    # Initialize execution state
    initial_exec_state = ExecutionState(target=deterministic_target)
    initial_state = OrchestrationState(
        execution_state=initial_exec_state,
        config=base_config,
        task_status={},
        errors={}
    )
    
    # Execute full pipeline
    config_run = {"configurable": {"thread_id": "e2e_success_thread"}}
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    final_state = app.invoke(graph_state_input, config=config_run)
    
    exec_state = final_state["execution_state"]
    
    orch_state = final_state["orchestration_state"]
    
    # Assert nodes executed
    assert "init" in orch_state.task_status
    assert "recon" in orch_state.task_status
    assert "js" in orch_state.task_status
    assert "api" in orch_state.task_status
    assert "vuln" in orch_state.task_status
    assert "analysis" in orch_state.task_status
    assert "report" in orch_state.task_status
    
    # Verify final execution state format
    assert isinstance(exec_state.recon_state.subdomains, tuple)
    assert isinstance(exec_state.recon_state.urls, tuple)
    assert isinstance(exec_state.findings, tuple)
    
    # Verify database persistence
    with get_db_session() as session:
        # Pipeline does not implement Storage layer population yet
        pass

    # Verify report generation is part of state
    assert len(exec_state.reports) == 2
    assert exec_state.reports[0].report_format.value == "markdown"
    assert exec_state.reports[1].report_format.value == "json"
