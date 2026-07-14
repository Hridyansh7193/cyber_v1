import pytest
from unittest.mock import patch

from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.checkpoint_manager import CheckpointManager


def test_checkpoint_with_intelligence(e2e_db, mock_subprocess_run, base_config, deterministic_target, tmp_path):
    cm = CheckpointManager(db_path=str(tmp_path / "checkpoints_intel.db"))
    app = build_graph(base_config, checkpointer=cm)
    
    initial_exec_state = ExecutionState(target=deterministic_target)
    initial_state = OrchestrationState(
        execution_state=initial_exec_state,
        config=base_config,
        task_status={},
        errors={}
    )
    
    config_run = {"configurable": {"thread_id": "e2e_checkpoint_intel"}}
    graph_state_input = {
        "execution_state": initial_exec_state,
        "orchestration_state": initial_state
    }
    
    # We will let the graph run until report_node.
    # We mock generate_reports to crash on the first run.
    
    def crash_report(state, config):
        raise ValueError("Simulated Report Crash")

    from agents.deltas.intelligence_delta import IntelligenceDelta
    from schemas.intelligence import IntelligenceState
    from orchestrator.delta_applier import apply_intelligence_delta

    def fake_analyze(state, config):
        return IntelligenceDelta(intelligence=IntelligenceState(version=99))

    with patch("orchestrator.nodes.report_node.generate_reports", side_effect=crash_report), \
         patch("orchestrator.nodes.analysis_node.analyze_intelligence", side_effect=fake_analyze), \
         patch("orchestrator.nodes.analysis_node.apply_finding_delta", new=apply_intelligence_delta):
        with pytest.raises(Exception, match="Simulated Report Crash"):
            app.invoke(graph_state_input, config=config_run)
            
    latest_checkpoint = app.get_state(config_run)
    state_before_crash = latest_checkpoint.values["execution_state"]
    
    # Ensure intelligence was generated before the crash
    assert state_before_crash.intelligence is not None
    assert state_before_crash.intelligence.version == 99
    
    # Second run: Graph resumes, Report succeeds
    # We don't patch report_node this time so it succeeds normally
    final_state = app.invoke(None, config=config_run)
    
    state_after_resume = final_state["execution_state"]
    
    # Verify exact match between state_before_crash and state_after_resume for intelligence
    intel_before = state_before_crash.intelligence
    intel_after = state_after_resume.intelligence
    
    assert intel_before is not None
    assert intel_after is not None
    
    assert intel_before.version == intel_after.version
    assert intel_before.correlated_findings == intel_after.correlated_findings
    assert intel_before.prioritized_assets == intel_after.prioritized_assets
    assert intel_before.attack_graph == intel_after.attack_graph
    assert intel_before.risk_summary == intel_after.risk_summary
    
    # The entire model_dump should be essentially identical for the intelligence block
    assert intel_before.model_dump_json() == intel_after.model_dump_json()

