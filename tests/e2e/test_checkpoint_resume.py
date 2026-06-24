import pytest

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
    
    config_run = {"configurable": {"thread_id": "e2e_checkpoint_thread"}}
    
    # We can't trivially interrupt a synchronous graph execution midway unless we use a conditional breakpoint or error.
    # We will simulate an error in RECON to stop the graph, then fix it and resume.
    
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # First Run: Mock fails in RECON
    with pytest.raises(Exception): # Let's simulate a hard fail inside the node by patching it
        from unittest.mock import patch
        with patch('orchestrator.nodes.recon_node.analyze_recon', side_effect=ValueError("Simulated Crash")):
            app.invoke(graph_state_input, config=config_run)
            
    # The checkpoint should have saved the state up to INIT
    # Second Run: Graph resumes
    # State should fetch from DB automatically if we pass None or empty state, but langgraph invoke with same thread will use checkpoint.
    # We invoke with None
    final_state = app.invoke(None, config=config_run)
    
    exec_state = final_state["execution_state"]
    
    orch_state = final_state["orchestration_state"]
    
    # Should have completed everything successfully now
    assert "report" in orch_state.task_status
    assert orch_state.task_status["report"] == "COMPLETED"
