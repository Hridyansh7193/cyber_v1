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
    
    wrapper_calls = {"recon": 0, "js": 0, "api": 0, "vuln": 0}
    
    from orchestrator.nodes.recon_node import dummy_recon_wrapper
    from orchestrator.nodes.js_node import dummy_js_wrapper
    from orchestrator.nodes.api_node import dummy_api_wrapper
    from orchestrator.nodes.vulnerability_node import dummy_vuln_wrapper
    
    def count_recon(state):
        wrapper_calls["recon"] += 1
        return dummy_recon_wrapper(state)
        
    def count_js(state):
        wrapper_calls["js"] += 1
        return dummy_js_wrapper(state)
        
    def count_api(state):
        wrapper_calls["api"] += 1
        return dummy_api_wrapper(state)
        
    def crash_vuln(state):
        raise ValueError("Simulated Vuln Crash")
        
    def count_vuln(state):
        wrapper_calls["vuln"] += 1
        return dummy_vuln_wrapper(state)
    
    config_run = {"configurable": {"thread_id": "e2e_checkpoint_thread"}}
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # First Run: Vuln fails
    with patch("orchestrator.nodes.recon_node.dummy_recon_wrapper", side_effect=count_recon), \
         patch("orchestrator.nodes.js_node.dummy_js_wrapper", side_effect=count_js), \
         patch("orchestrator.nodes.api_node.dummy_api_wrapper", side_effect=count_api), \
         patch("orchestrator.nodes.vulnerability_node.dummy_vuln_wrapper", side_effect=crash_vuln):
        with pytest.raises(Exception):
            app.invoke(graph_state_input, config=config_run)
            
    assert wrapper_calls["recon"] == 1
    assert wrapper_calls["js"] == 1
    assert wrapper_calls["api"] == 1
    assert wrapper_calls["vuln"] == 0
            
    # Second Run: Graph resumes, Vuln succeeds
    with patch("orchestrator.nodes.recon_node.dummy_recon_wrapper", side_effect=count_recon), \
         patch("orchestrator.nodes.js_node.dummy_js_wrapper", side_effect=count_js), \
         patch("orchestrator.nodes.api_node.dummy_api_wrapper", side_effect=count_api), \
         patch("orchestrator.nodes.vulnerability_node.dummy_vuln_wrapper", side_effect=count_vuln):
        final_state = app.invoke(None, config=config_run)
    
    exec_state = final_state["execution_state"]
    orch_state = final_state["orchestration_state"]
    
    # Assert idempotency: all nodes executed exactly once
    assert wrapper_calls["recon"] == 1
    assert wrapper_calls["js"] == 1
    assert wrapper_calls["api"] == 1
    assert wrapper_calls["vuln"] == 1
    
    # Should have completed everything successfully now
    assert "report" in orch_state.task_status
    assert orch_state.task_status["report"] == "COMPLETED"
