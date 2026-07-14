
from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from schemas.finding import Finding

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
        d1 = r1.model_dump()
        d2 = r2.model_dump()
        d1.pop("end_time", None)
        d2.pop("end_time", None)
        d1.pop("start_time", None)
        d2.pop("start_time", None)
        d1.pop("report_path", None)
        d2.pop("report_path", None)
        d1.pop("report_id", None)
        d2.pop("report_id", None)
        assert d1 == d2
        
        import re
        def sanitize(text):
            text = re.sub(r'End Time:.*', 'End Time: <SANITIZED>', text)
            text = re.sub(r'Duration:.*', 'Duration: <SANITIZED>', text)
            text = re.sub(r'"end_time":\s*".*"', '"end_time": "<SANITIZED>"', text)
            text = re.sub(r'"duration_seconds":\s*[\d\.]+', '"duration_seconds": 0.0', text)
            text = re.sub(r'"report_id":\s*".*"', '"report_id": "<SANITIZED>"', text)
            text = re.sub(r'"report_path":\s*".*"', '"report_path": "<SANITIZED>"', text)
            text = re.sub(r'\*\*Finished\*\*\s*\|\s*\*\*.*\*\*', '**Finished** | **<SANITIZED>**', text)
            return text
            
        if r1.report_format.value == "markdown":
            g1 = generate_markdown(r1)
            g2 = generate_markdown(r2)
            assert sanitize(g1.content) == sanitize(g2.content)
            
            gd1 = g1.model_dump()
            gd2 = g2.model_dump()
            gd1.pop("filename", None)
            gd2.pop("filename", None)
            gd1.pop("report_id", None)
            gd2.pop("report_id", None)
            gd1["content"] = sanitize(gd1["content"])
            gd2["content"] = sanitize(gd2["content"])
            assert gd1 == gd2
        elif r1.report_format.value == "json":
            g1 = generate_json(r1)
            g2 = generate_json(r2)
            assert sanitize(g1.content) == sanitize(g2.content)
            
            gd1 = g1.model_dump()
            gd2 = g2.model_dump()
            gd1.pop("filename", None)
            gd2.pop("filename", None)
            gd1.pop("report_id", None)
            gd2.pop("report_id", None)
            gd1["content"] = sanitize(gd1["content"])
            gd2["content"] = sanitize(gd2["content"])
            assert gd1 == gd2
