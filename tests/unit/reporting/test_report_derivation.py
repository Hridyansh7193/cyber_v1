from agents.reporter_agent import generate_reports
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.telemetry import ExecutionTelemetry
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from datetime import datetime, timezone


def _make_config():
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )


def test_live_report_derives_plugins_from_telemetry():
    t_state = TargetState(domain="test.com", session_id="abc", start_time=datetime.now(timezone.utc))
    logs = (
        ExecutionTelemetry(tool="httpx", version="1.0", command="httpx", execution_time=1.2, exit_code=0, success=True, parsed_objects=5, stdout_size=1, stderr_size=0, timeout=False, wrapper_errors=(), parser_errors=(), binary_path="", working_directory=""),
        ExecutionTelemetry(tool="katana", version="1.0", command="katana", execution_time=2.3, exit_code=1, success=False, parsed_objects=0, stdout_size=1, stderr_size=0, timeout=False, wrapper_errors=(), parser_errors=(), binary_path="", working_directory="")
    )
    state = ExecutionState(target=t_state, logs=logs)
    config = _make_config()

    delta = generate_reports(state, config)
    report = delta.reports[0]

    assert len(report.plugin_summaries) == 2
    assert report.plugin_summaries[0].plugin == "httpx"
    assert report.plugin_summaries[0].status == "PASS"
    assert report.plugin_summaries[1].plugin == "katana"
    assert report.plugin_summaries[1].status == "FAIL"


def test_cli_and_json_error_count_agree():
    t_state = TargetState(domain="test.com", session_id="abc", start_time=datetime.now(timezone.utc))
    logs = (
        ExecutionTelemetry(tool="katana", version="1.0", command="katana", execution_time=2.3, exit_code=1, success=False, parsed_objects=0, stdout_size=1, stderr_size=0, timeout=False, wrapper_errors=(), parser_errors=(), binary_path="", working_directory=""),
    )
    state = ExecutionState(target=t_state, logs=logs)
    config = _make_config()

    delta = generate_reports(state, config)
    report = delta.reports[0]

    assert report.error_count == 1
    assert "katana" in report.failed_plugins
    assert report.status == "FAIL"


def test_duration_and_timestamps_populated():
    t_state = TargetState(domain="test.com", session_id="abc", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=t_state)
    config = _make_config()

    delta = generate_reports(state, config)
    report = delta.reports[0]

    assert report.duration.endswith("s")
    assert report.start_time != ""
    assert report.end_time != ""


def test_measured_metrics_population():
    t_state = TargetState(domain="test.com", session_id="abc", start_time=datetime.now(timezone.utc))
    logs = (
        ExecutionTelemetry(tool="httpx", version="1.0", command="httpx", execution_time=1.2, exit_code=0, success=True, parsed_objects=3, stdout_size=1, stderr_size=0, timeout=False, wrapper_errors=(), parser_errors=(), binary_path="", working_directory=""),
    )
    state = ExecutionState(target=t_state, logs=logs)
    config = _make_config()

    delta = generate_reports(state, config)
    report = delta.reports[0]

    assert "alive_hosts" in report.assets.measured_metrics
    assert "urls" not in report.assets.measured_metrics
