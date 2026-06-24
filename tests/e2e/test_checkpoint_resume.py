import pytest
from unittest.mock import patch

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.checkpoint_manager import CheckpointManager

def test_checkpoint_resume(e2e_db, mock_subprocess_run, base_config, deterministic_target, tmp_path):
    # This requires the real SqliteSaver attached to the graph
    cm = CheckpointManager(db_path=str(tmp_path / "checkpoints.db"))
    app = build_graph(base_config, checkpointer=cm)
    
    initial_exec_state = ExecutionState(target=deterministic_target)
    initial_state = OrchestrationState(
        execution_state=initial_exec_state,
        config=base_config,
        task_status={},
        errors={}
    )
    
    wrapper_calls = {"recon": 0, "js": 0, "api": 0}
    
    from schemas.tool_result import ToolResult
    
    def mock_recon(state):
        wrapper_calls["recon"] += 1
        return ToolResult(tool_name="dummy", metadata={"new_subdomains": [], "new_hosts": [], "new_urls": []}, errors=[], success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)
        
    def mock_js(state):
        wrapper_calls["js"] += 1
        return ToolResult(tool_name="dummy", metadata={"new_js_files": [], "new_endpoints": []}, errors=[], success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)
        
    def mock_api_fail(state):
        wrapper_calls["api"] += 1
        raise ValueError("Simulated API Crash")
        
    def mock_api_success(state):
        wrapper_calls["api"] += 1
        return ToolResult(tool_name="dummy", metadata={"new_swagger_urls": [], "new_graphql_urls": []}, errors=[], success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)
    
    config_run = {"configurable": {"thread_id": "e2e_checkpoint_thread"}}
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # First Run: API fails
    with patch("orchestrator.nodes.recon_node.dummy_recon_wrapper", side_effect=mock_recon), \
         patch("orchestrator.nodes.js_node.dummy_js_wrapper", side_effect=mock_js), \
         patch("orchestrator.nodes.api_node.dummy_api_wrapper", side_effect=mock_api_fail):
        with pytest.raises(Exception):
            app.invoke(graph_state_input, config=config_run)
            
    assert wrapper_calls["recon"] == 1
    assert wrapper_calls["js"] == 1
    assert wrapper_calls["api"] == 1
            
    # Second Run: Graph resumes, API succeeds
    with patch("orchestrator.nodes.recon_node.dummy_recon_wrapper", side_effect=mock_recon), \
         patch("orchestrator.nodes.js_node.dummy_js_wrapper", side_effect=mock_js), \
         patch("orchestrator.nodes.api_node.dummy_api_wrapper", side_effect=mock_api_success):
        final_state = app.invoke(None, config=config_run)
    
    exec_state = final_state["execution_state"]
    orch_state = final_state["orchestration_state"]
    
    # Assert idempotency: recon and JS were NOT run again
    assert wrapper_calls["recon"] == 1
    assert wrapper_calls["js"] == 1
    assert wrapper_calls["api"] == 2
    
    # Should have completed everything successfully now
    assert "report" in orch_state.task_status
    assert orch_state.task_status["report"] == "COMPLETED"
