import pytest
from unittest.mock import patch
from execution.plugin_executor import PluginExecutor
from config.schemas import BugHunterConfig
from schemas.tool_result import ToolResult
from execution.utils.process_runner import ProcessResult

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_plugin_executor_recon(mock_run):
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout="sub1.example.com",
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
    results = PluginExecutor.execute_plugins(("subfinder",), config, "example.com", result_key="new_findings")
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "subfinder"
    assert "sub1.example.com" in results[0].metadata["new_findings"]

@patch("execution.utils.process_runner.ProcessRunner.run")
def test_plugin_executor_js(mock_run):
    mock_run.return_value = ProcessResult(
        exit_code=0,
        stdout="endpoint1.js",
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
    results = PluginExecutor.execute_plugins(("linkfinder",), config, "example.com", result_key="new_endpoints")
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "linkfinder"
    assert "endpoint1.js" in results[0].metadata["new_endpoints"]

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
    results = PluginExecutor.execute_plugins(("nuclei",), config, "example.com", result_key="new_vulnerabilities")
    
    assert len(results) == 1
    assert results[0].success
    assert results[0].tool_name == "nuclei"
    assert results[0].metadata["new_vulnerabilities"][0]["template-id"] == "cve-1234"
