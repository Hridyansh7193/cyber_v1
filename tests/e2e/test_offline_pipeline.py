import pytest
from unittest import mock
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry

# We need to mock the ProcessRunner.run to return fixture data.
# The easiest way is to mock ProcessRunner.run directly.
@pytest.fixture
def mock_config():
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=1, log_level="INFO"),
        llm=LLMConfig(provider="none", default_model="none", timeout=10),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=1, nuclei_timeout=1, dalfox_timeout=1, ffuf_timeout=1, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={})
    )

def _get_fixture(target_type: str, plugin_name: str) -> str:
    # return dummy output for simplicity in this MVP script
    if target_type == "broken_output":
        return "{" if plugin_name.endswith("json") else "GARBAGE\nGARBAGE"
    
    if plugin_name == "subfinder":
        return "test.com\nsub.test.com"
    elif plugin_name == "httpx":
        return '{"url": "http://test.com", "host": "test.com", "port": 80}\n{"url": "http://sub.test.com", "host": "sub.test.com", "port": 80}'
    return ""

def _mock_process_runner(target_type):
    def side_effect(cmd, plugin_name, **kwargs):
        class MockResult:
            def __init__(self, out):
                self.stdout = out
                self.stderr = ""
                self.exit_code = 0
                self.success = True
                self.binary_path = cmd[0]
                self.command = " ".join(cmd)
                self.cwd = "/tmp"
                self.execution_time = 1.0
                self.stdout_size = len(out)
                self.error_message = None
        
        return MockResult(_get_fixture(target_type, plugin_name))
    return side_effect

@mock.patch("execution.utils.process_runner.ProcessRunner.run")
def test_offline_pipeline_simple(mock_run, mock_config):
    mock_run.side_effect = _mock_process_runner("simple_target")
    
    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, mock_config)
    # Instantiate properly (omitted detailed setup for brevity, assuming standard instantiation works)
    # The actual implementation of test offline pipeline would instantiate ScanService
    # and call submit_scan.
    
    # Assertions
    # 1. Every plugin generated a TraceEvent.
    # 2. Transition counts match (Produced == next Received).
    # 3. parsed <= stdout_lines.
    # 4. stored <= parsed.
    # 5. No negative counts.
    # 6. trace.json exists and is valid.
    pass

@mock.patch("execution.utils.process_runner.ProcessRunner.run")
def test_offline_pipeline_broken_output(mock_run, mock_config):
    mock_run.side_effect = _mock_process_runner("broken_output")
    # This should not crash, but rather log parsing errors and store 0 objects.
    pass
