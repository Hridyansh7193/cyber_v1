from pathlib import Path

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from storage.database import get_db_session


def test_full_pipeline_success(e2e_db, mock_subprocess_run, base_config, deterministic_target, tmp_path):
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
    assert "passive_recon" in orch_state.task_status
    assert "scope_enforcement" in orch_state.task_status
    assert "active_recon" in orch_state.task_status
    assert "js" in orch_state.task_status
    assert "api" in orch_state.task_status
    assert "parameter" in orch_state.task_status
    assert "vulnerability" in orch_state.task_status
    assert "analysis" in orch_state.task_status
    assert "report" in orch_state.task_status
    
    # Verify final execution state format
    assert isinstance(exec_state.recon_state.subdomains, tuple)
    assert isinstance(exec_state.recon_state.urls, tuple)
    assert isinstance(exec_state.findings, tuple)
    
    # Verify database persistence via public interfaces
    from storage.repositories.target_repository import TargetRepository
    from storage.repositories.finding_repository import FindingRepository
    from storage.repositories.report_repository import ReportRepository
    
    with get_db_session() as session:
        target_repo = TargetRepository()
        finding_repo = FindingRepository()
        report_repo = ReportRepository()
        
        # Test persistence
        saved_target = target_repo.create(session, exec_state.target)
        assert saved_target.domain == exec_state.target.domain
        
        # Test retrieval
        retrieved_target = target_repo.get_by_domain(session, exec_state.target.domain)
        assert retrieved_target is not None
        assert retrieved_target.domain == exec_state.target.domain
        
        # Persist findings
        finding_repo.create_bulk(session, exec_state.target.session_id, exec_state.findings)
        retrieved_findings = finding_repo.get_by_session(session, exec_state.target.session_id)
        assert len(retrieved_findings) == len(exec_state.findings)
        for finding in exec_state.findings:
            assert any(f.title == finding.title for f in retrieved_findings)
            
        # Persist reports
        # The ReportRepository bulk API expects Iterable[Report] and uses r.session_id
        # We ensure they match or update if needed, but orchestrator sets it.
        report_repo.create_bulk(session, exec_state.reports)
        retrieved_reports = report_repo.get_by_session(session, exec_state.target.session_id)
        assert len(retrieved_reports) == len(exec_state.reports)
        for report in exec_state.reports:
            assert any(r.report_path == report.report_path for r in retrieved_reports)

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
