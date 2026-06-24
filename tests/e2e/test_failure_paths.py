import pytest
import subprocess
from unittest.mock import patch
from pydantic import ValidationError

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState

def test_failure_path_timeout(e2e_db, base_config, deterministic_target):
    # Inject TimeoutExpired into subprocess
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["nuclei"], 300)) as mock_run:
        app = build_graph(base_config)
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=base_config,
            task_status={},
            errors={}
        )
        
        config_run = {"configurable": {"thread_id": "e2e_timeout_thread"}}
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        final_state = app.invoke(graph_state_input, config=config_run)
        
        exec_state = final_state["execution_state"]
        
        orch_state = final_state["orchestration_state"]
        
        # Recon should have failed gracefully due to timeout
        # Tool results should capture the exit_code = -1
        assert "recon" in orch_state.task_status
        assert orch_state.task_status["recon"] in ["COMPLETED", "FAILED"]

def test_failure_path_oserror(e2e_db, base_config, deterministic_target):
    with patch("subprocess.run", side_effect=OSError("Permission denied")) as mock_run:
        app = build_graph(base_config)
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=base_config,
            task_status={},
            errors={}
        )
        
        config_run = {"configurable": {"thread_id": "e2e_oserror_thread"}}
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        final_state = app.invoke(graph_state_input, config=config_run)
        
        exec_state = final_state["execution_state"]
        
        orch_state = final_state["orchestration_state"]
        
        assert "recon" in orch_state.task_status

def test_failure_path_malformed_json(e2e_db, fixtures_dir, base_config, deterministic_target):
    # Return malformed JSON for a tool
    def side_effect(cmd, *args, **kwargs):
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="not_a_json_object", stderr="")

    with patch("subprocess.run", side_effect=side_effect):
        app = build_graph(base_config)
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state, 
            config=base_config,
            task_status={},
            errors={}
        )
        
        config_run = {"configurable": {"thread_id": "e2e_malformed_thread"}}
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        final_state = app.invoke(graph_state_input, config=config_run)
        
        # Should gracefully handle parsing failure and output empty results instead of crashing the orchestrator
        exec_state = final_state["execution_state"]
        assert len(exec_state.findings) == 0

def test_adversarial_invalid_schemas(base_config):
    # Bypassing the graph to test strict boundaries
    from schemas.target import TargetState
    with pytest.raises(ValidationError):
        TargetState(
            domain="example.com",
            scope=[],
            session_id=None, # Invalid
            start_time="not-a-datetime"
        )
