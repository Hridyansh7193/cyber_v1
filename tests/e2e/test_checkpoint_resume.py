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
    
    from execution.plugin_executor import PluginExecutor
    
    def count_recon(*args, **kwargs):
        wrapper_calls["recon"] += 1
        return tuple()
        
    def count_js(*args, **kwargs):
        wrapper_calls["js"] += 1
        return tuple()
        
    def count_api(*args, **kwargs):
        wrapper_calls["api"] += 1
        return tuple()
        
    def crash_vuln(*args, **kwargs):
        raise ValueError("Simulated Vuln Crash")
        
    def count_vuln(*args, **kwargs):
        wrapper_calls["vuln"] += 1
        return tuple()
    
    config_run = {"configurable": {"thread_id": "e2e_checkpoint_thread"}}
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # First Run: Vuln fails
    with patch("execution.wrappers.ReconWrapper.execute", side_effect=count_recon), \
         patch("execution.wrappers.JSWrapper.execute", side_effect=count_js), \
         patch("execution.wrappers.APIWrapper.execute", side_effect=count_api), \
         patch("execution.wrappers.VulnWrapper.execute", side_effect=crash_vuln):
        with pytest.raises(Exception):
            app.invoke(graph_state_input, config=config_run)
            
    assert wrapper_calls["recon"] == 1
    assert wrapper_calls["js"] == 1
    assert wrapper_calls["api"] == 1
    assert wrapper_calls["vuln"] == 0
            
    # Second Run: Graph resumes, Vuln succeeds
    with patch("execution.wrappers.ReconWrapper.execute", side_effect=count_recon), \
         patch("execution.wrappers.JSWrapper.execute", side_effect=count_js), \
         patch("execution.wrappers.APIWrapper.execute", side_effect=count_api), \
         patch("execution.wrappers.VulnWrapper.execute", side_effect=count_vuln):
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
