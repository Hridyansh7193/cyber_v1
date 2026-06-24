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
    
    # Verify database persistence via public interfaces
    from storage.repositories.target_repository import TargetRepository
    
    with get_db_session() as session:
        repo = TargetRepository()
        
        # Test persistence
        saved_target = repo.create(session, exec_state.target)
        assert saved_target.domain == "example.com"
        
        # Test retrieval
        retrieved_target = repo.get_by_domain(session, "example.com")
        assert retrieved_target is not None
        assert retrieved_target.domain == "example.com"

    # Verify report generation is part of state
    assert len(exec_state.reports) == 2
    assert exec_state.reports[0].report_format.value == "markdown"
    assert exec_state.reports[1].report_format.value == "json"
    
    # Verify file storage through public interface
    from storage.file_storage import save_generated_file
    from reporting.markdown_renderer import generate_markdown
    from reporting.json_renderer import generate_json
    
    for report in exec_state.reports:
        fmt_str = report.report_format.value
        if fmt_str == "markdown":
            g_rep = generate_markdown(report)
        else:
            g_rep = generate_json(report)
            
        output_dir = Path(base_config.reporting.output_directories[fmt_str])
        saved_path = save_generated_file(g_rep, output_dir)
        assert Path(saved_path).exists()
        assert Path(saved_path).is_file()
