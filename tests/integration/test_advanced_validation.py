import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from schemas.state import ExecutionState, ReconState
from schemas.target import TargetState
from config.schemas import BugHunterConfig
from execution.plugin_executor import PluginExecutor
from schemas.runtime_context import RuntimeContext
from services.tool_manager import ToolManager
from services.target_resolver import TargetResolver

@pytest.fixture
def base_config():
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )

@pytest.fixture
def mock_runtime_context():
    tm = ToolManager()
    tr = TargetResolver()
    
    # Mock tool manager to return specific info
    with patch.object(tm, "get_tool") as mock_get_tool:
        yield RuntimeContext(
            tool_manager=tm,
            target_resolver=tr,
            wordlist_manager=None
        )

def test_missing_binary(base_config, mock_runtime_context):
    mock_runtime_context.tool_manager.get_tool.return_value = None
    target = TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=target, runtime_context=mock_runtime_context)
    
    results = PluginExecutor.execute_plugins(("subfinder",), base_config, state)
    
    # If binary is missing, it should skip execution and return empty results for that plugin
    assert len(results) == 0

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_invalid_json_output(mock_run, base_config, mock_runtime_context):
    from execution.utils.process_runner import ProcessResult
    
    # Mock a tool returning valid result, but invalid JSON output
    from services.tool_manager import ToolInfo
    mock_runtime_context.tool_manager.get_tool.return_value = ToolInfo(name="subfinder", binary_path="/mock/subfinder", installed=True)
    
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout="{invalid_json}",
        stderr="",
        execution_time=1.0,
        command="/mock/subfinder -d example.com",
        binary_path="/mock/subfinder",
        cwd="/tmp"
    )
    
    target = TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=target, runtime_context=mock_runtime_context)
    
    results = PluginExecutor.execute_plugins(("subfinder",), base_config, state)
    
    # Subfinder parse skips invalid JSON and treats it as raw text if it doesn't have spaces
    # In this case {invalid_json} doesn't have space and no dot, so it shouldn't be added
    assert len(results) == 1
    assert len(results[0].metadata.get("new_subdomains", [])) == 0

def test_target_extraction(base_config, mock_runtime_context):
    # Test if PluginExecutor correctly extracts targets
    from services.tool_manager import ToolInfo
    mock_runtime_context.tool_manager.get_tool.return_value = ToolInfo(name="httpx", binary_path="/mock/httpx", installed=True)
    
    target = TargetState(session_id="test", domain="example.com", start_time=datetime.now(timezone.utc))
    recon_state = ReconState(subdomains=("sub1.example.com", "sub2.example.com"))
    state = ExecutionState(target=target, recon_state=recon_state, runtime_context=mock_runtime_context)
    
    with patch("execution.utils.process_runner.ProcessRunner.run") as mock_run:
        from execution.utils.process_runner import ProcessResult
        mock_run.return_value = ProcessResult(
            exit_code=0,
            stdout="",
            stderr="",
            execution_time=1.0,
            command="",
            binary_path="/mock/httpx",
            cwd="/tmp"
        )
        
        PluginExecutor.execute_plugins(("httpx",), base_config, state)
        
        # Check that -l was appended with a temp file
        called_cmd = mock_run.call_args[0][0]
        assert "-l" in called_cmd
        
        # Test fallback to single target if no subdomains
        state2 = state.model_copy(update={"recon_state": ReconState(subdomains=())})
        PluginExecutor.execute_plugins(("httpx",), base_config, state2)
        called_cmd2 = mock_run.call_args[0][0]
        assert "-u" in called_cmd2
        assert "example.com" in called_cmd2
