import pytest
from pathlib import Path
import hashlib
from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from config.schemas import BugHunterConfig

@pytest.mark.skip(reason="Needs update for Milestone 3 TaskQueue orchestration logic")
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
    assert state1.model_dump() == state2.model_dump()

    # 2. Reports Identical
    assert content1["markdown"] == content2["markdown"]
    assert content1["json"] == content2["json"]

    # 3. Check Hashes
    md_hash1 = hashlib.sha256(content1["markdown"].encode('utf-8')).hexdigest()
    md_hash2 = hashlib.sha256(content2["markdown"].encode('utf-8')).hexdigest()
    assert md_hash1 == md_hash2

    json_hash1 = hashlib.sha256(content1["json"].encode('utf-8')).hexdigest()
    json_hash2 = hashlib.sha256(content2["json"].encode('utf-8')).hexdigest()
    assert json_hash1 == json_hash2
