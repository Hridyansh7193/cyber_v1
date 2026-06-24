import pytest
import subprocess
from unittest.mock import patch
from pydantic import ValidationError

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState

def test_failure_path_timeout(e2e_db, base_config, deterministic_target):
    # Inject TimeoutExpired into ProcessRunner
    with patch("execution.utils.process_runner.ProcessRunner.run", side_effect=subprocess.TimeoutExpired(["nuclei"], 300)) as mock_run:
        from orchestrator.nodes.recon_node import recon_node
        from orchestrator.node_result import NodeResult
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=base_config,
            task_status={},
            errors={}
        )
        
        node_result = NodeResult(execution_state=initial_exec_state, orchestration_state=initial_state)
        
        pre_failure_state = node_result.execution_state.model_dump()
        
        result = recon_node(node_result, base_config)
        
        # Tool results should capture the timeout gracefully, or the wrapper handles it, but let's assert the previous state is untouched.
        assert result.execution_state.target.model_dump() == pre_failure_state["target"]
        assert "recon" in result.orchestration_state.task_status

def test_failure_path_oserror(e2e_db, base_config, deterministic_target):
    with patch("execution.utils.process_runner.ProcessRunner.run", side_effect=OSError("Permission denied")) as mock_run:
        from orchestrator.nodes.recon_node import recon_node
        from orchestrator.node_result import NodeResult
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=base_config,
            task_status={},
            errors={}
        )
        
        node_result = NodeResult(execution_state=initial_exec_state, orchestration_state=initial_state)
        
        pre_failure_state = node_result.execution_state.model_dump()
        
        result = recon_node(node_result, base_config)
        
        assert result.execution_state.target.model_dump() == pre_failure_state["target"]
        assert "recon" in result.orchestration_state.task_status

def test_failure_path_malformed_json(e2e_db, fixtures_dir, base_config, deterministic_target):
    # Return malformed JSON for a tool
    def side_effect(command, tool_name, cwd=None):
        return (0, "not_a_json_object", "", 1.0)

    with patch("execution.utils.process_runner.ProcessRunner.run", side_effect=side_effect):
        from orchestrator.nodes.recon_node import recon_node
        from orchestrator.node_result import NodeResult
        
        initial_exec_state = ExecutionState(target=deterministic_target)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state, 
            config=base_config,
            task_status={},
            errors={}
        )
        
        node_result = NodeResult(execution_state=initial_exec_state, orchestration_state=initial_state)
        
        pre_failure_state = node_result.execution_state.model_dump()
        
        result = recon_node(node_result, base_config)
        
        # Should gracefully handle parsing failure and output empty results instead of crashing the orchestrator
        assert len(result.execution_state.findings) == 0
        assert result.execution_state.target.model_dump() == pre_failure_state["target"]

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
