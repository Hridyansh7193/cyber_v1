import pytest
from unittest.mock import patch
from execution.plugin_executor import PluginExecutor
from config.schemas import BugHunterConfig
from schemas.tool_result import ToolResult
from schemas.state import ExecutionState
from schemas.target import TargetState
from datetime import datetime, timezone
from execution.utils.process_runner import ProcessResult

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_plugin_executor_recon(mock_run):
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout='{"host": "sub1.example.com"}',
        stderr="",
        execution_time=1.0,
        command="subfinder -d example.com",
        binary_path="/usr/bin/subfinder",
        cwd="/tmp"
    )
    
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    
    import uuid
    target = TargetState(session_id=uuid.uuid4().hex, domain="example.com", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=target)
    results = PluginExecutor.execute_plugins(("subfinder",), config, state)
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "subfinder"
    assert "sub1.example.com" in results[0].metadata["new_subdomains"]

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_plugin_executor_js(mock_run):
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout="http://example.com/endpoint1.js",
        stderr="",
        execution_time=1.0,
        command="linkfinder -i example.com",
        binary_path="/usr/bin/linkfinder",
        cwd="/tmp"
    )
    
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    
    import uuid
    target = TargetState(session_id=uuid.uuid4().hex, domain="example.com", start_time=datetime.now(timezone.utc))
    from schemas.state import JSState
    state = ExecutionState(target=target, js_state=JSState(js_files=("http://example.com/app.js",)))
    results = PluginExecutor.execute_plugins(("linkfinder",), config, state)
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "linkfinder"
    assert "http://example.com/endpoint1.js" in results[0].metadata["new_endpoints"]

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_plugin_executor_vuln(mock_run):
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout='{"template-id": "cve-1234"}',
        stderr="",
        execution_time=1.0,
        command="nuclei -u example.com",
        binary_path="/usr/bin/nuclei",
        cwd="/tmp"
    )
    
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    
    import uuid
    target = TargetState(session_id=uuid.uuid4().hex, domain="example.com", start_time=datetime.now(timezone.utc))
    from schemas.state import ReconState
    state = ExecutionState(target=target, recon_state=ReconState(urls=("http://example.com",)))
    results = PluginExecutor.execute_plugins(("nuclei",), config, state)
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "nuclei"
    assert results[0].metadata["new_nuclei"][0]["template-id"] == "cve-1234"
