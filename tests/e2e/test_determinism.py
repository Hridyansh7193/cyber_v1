from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState


def test_pipeline_determinism(e2e_db, mock_subprocess_run, base_config, deterministic_target, tmp_path):
    def run_pipeline(thread_id):
        app = build_graph(base_config)
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=base_config,
            task_status={},
            errors={}
        )
        
        config_run = {"configurable": {"thread_id": thread_id}}
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        final_state = app.invoke(graph_state_input, config=config_run)
        
        exec_state = final_state["execution_state"]
        
        # Read the generated markdown and json reports
        from reporting.markdown_renderer import generate_markdown
        from reporting.json_renderer import generate_json
        
        reports_content = {}
        for report in exec_state.reports:
            if report.report_format.value == "markdown":
                reports_content["markdown"] = generate_markdown(report).content
            else:
                reports_content["json"] = generate_json(report).content
                
        return exec_state, reports_content

    state1, content1 = run_pipeline("thread_1")
    state2, content2 = run_pipeline("thread_2")

    # 1. ExecutionState Identical
    # Pydantic models can be compared directly
    # Wait, the target has a UUID session_id? `deterministic_target` fixes it.
    dump1 = state1.model_dump()
    dump2 = state2.model_dump()
    
    # Remove volatile fields
    for d in [dump1, dump2]:
        if d.get("target"):
            d["target"].pop("end_time", None)
            d["target"].pop("start_time", None)
        for r in d.get("reports", []):
            r.pop("report_path", None)
            r.pop("report_id", None)
            r.pop("start_time", None)
            r.pop("end_time", None)
            
    assert dump1 == dump2

    # 2. Reports Identical
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
        
    assert sanitize(content1["markdown"]) == sanitize(content2["markdown"])
    assert sanitize(content1["json"]) == sanitize(content2["json"])
