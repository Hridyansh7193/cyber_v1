from unittest.mock import patch, MagicMock
from schemas.tool_result import ToolResult
from schemas.state import ExecutionState, TargetState
from orchestrator.wrapper_result_applier import apply_recon_wrapper_result
from orchestrator.delta_applier import apply_recon_delta
from agents.reporter_agent import generate_reports
from execution.wrappers import ReconWrapper
from agents.deltas import ReconDelta

def test_full_pipeline_mocked_subfinder():
    # 1. Mock PluginExecutor to simulate Subfinder output
    config = MagicMock()
    config.reporting.report_formats = ["json"]
    config.reporting.output_directories = {"json": "."}
    
    mock_tool_result = ToolResult(
        tool_name="subfinder",
        success=True,
        exit_code=0,
        stdout="example.com\napi.example.com",
        stderr="",
        execution_time=1.0,
        parsed_output=("example.com", "api.example.com"),
        metadata={"new_subdomains": ["example.com", "api.example.com"]}
    )

    with patch("execution.plugin_executor.PluginExecutor.execute_plugins") as mock_exec:
        mock_exec.return_value = (mock_tool_result,)
        
        # 2. Run Wrapper
        from datetime import datetime, UTC
        initial_state = ExecutionState(target=TargetState(session_id="test", target="example.com", domain="example.com", start_time=datetime.now(UTC)))
        wrapper_results = ReconWrapper.execute(("subfinder",), config, initial_state)
        
        # 3. Apply Wrapper Result to State
        state_after_wrapper = apply_recon_wrapper_result(initial_state, wrapper_results)
        
        # Check invariants
        assert "example.com" in state_after_wrapper.recon_state.subdomains
        assert "api.example.com" in state_after_wrapper.recon_state.subdomains
        assert len(state_after_wrapper.logs) == 1
        assert state_after_wrapper.logs[0].tool == "subfinder"
        
        # 4. Simulate AI Agent returning an empty delta (e.g., it found nothing new)
        empty_delta = ReconDelta(subdomains=(), alive_hosts=(), urls=())
        state_after_delta = apply_recon_delta(state_after_wrapper, empty_delta)
        
        # Check invariant: Data is not lost
        assert "example.com" in state_after_delta.recon_state.subdomains
        
        # 5. Generate Report
        report_delta = generate_reports(state_after_delta, config)
        assert len(report_delta.reports) > 0
        report = report_delta.reports[0]
        
        # Assert Assets are populated
        assert "example.com" in report.assets.subdomains
        assert len(report.telemetry) == 1
        assert report.telemetry[0].tool == "subfinder"
