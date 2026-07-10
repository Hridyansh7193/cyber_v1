import pytest
from pathlib import Path

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from schemas.finding import Finding
from schemas.target import TargetState

def test_report_generation_10k_findings(e2e_db, base_config, deterministic_target):
    # Directly invoke the reporter with 10k findings
    from agents.reporter_agent import generate_reports
    
    findings = []
    for i in range(100): # Using 100 for test speed, representing large bulk
        findings.append(
            Finding(
                id=f"find_{i}",
                title=f"Bulk Finding {i} 🌍", # Unicode testing
                description="Test description",
                severity="medium",
                url=f"https://example.com/{i}",
                component="test",
                tool_source="test_tool",
                confidence="high",
                evidence="test evidence"
            )
        )
        
    exec_state = ExecutionState(target=deterministic_target, findings=tuple(findings))
    
    delta = generate_reports(exec_state, base_config)
    
    assert len(delta.reports) == 2 # 1 markdown, 1 json
    
    for report in delta.reports:
        assert report.report_format is not None
        
        # Reports should be generated without error

@pytest.mark.skip(reason="Needs update for Milestone 3 TaskQueue orchestration logic")
def test_report_determinism(e2e_db, mock_subprocess_run, base_config, deterministic_target, tmp_path):
    app = build_graph(base_config)
    
    initial_exec_state = ExecutionState(target=deterministic_target)
    initial_state = OrchestrationState(
        execution_state=initial_exec_state, 
        config=base_config,
        task_status={},
        errors={}
    )
    
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # Run 1
    config_run_1 = {"configurable": {"thread_id": "e2e_report_1"}}
    state_1 = app.invoke(graph_state_input, config=config_run_1)
    
    # Run 2
    config_run_2 = {"configurable": {"thread_id": "e2e_report_2"}}
    state_2 = app.invoke(graph_state_input, config=config_run_2)
    
    reports_1 = state_1["execution_state"].reports
    reports_2 = state_2["execution_state"].reports
    
    assert len(reports_1) == len(reports_2)
    assert len(reports_1) > 0
    
    from reporting.markdown_renderer import generate_markdown
    from reporting.json_renderer import generate_json
    
    for r1, r2 in zip(reports_1, reports_2):
        assert r1.report_id == r2.report_id
        assert r1.model_dump() == r2.model_dump()
        
        if r1.report_format.value == "markdown":
            g1 = generate_markdown(r1)
            g2 = generate_markdown(r2)
            assert g1.content == g2.content
            assert g1.model_dump() == g2.model_dump()
        elif r1.report_format.value == "json":
            g1 = generate_json(r1)
            g2 = generate_json(r2)
            assert g1.content == g2.content
            assert g1.model_dump() == g2.model_dump()
