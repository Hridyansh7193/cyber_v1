from schemas.state import ExecutionState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from schemas.target import TargetState
from agents.planner_agent import plan
from datetime import datetime, timezone

def test_planner_agent():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    
    # 1. Test full run (no existing recon data)
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    delta = plan(state, config)
    tasks = [t.name for t in delta.task_queue]
    
    assert "node:passive_recon_node" in tasks
    assert "node:js_node" in tasks
    assert "node:api_node" in tasks
    assert "node:vulnerability_node" in tasks
    
    # 2. Test JS/API disabled
    config_disabled = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={"js": False, "api": False}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    delta_disabled = plan(state, config_disabled)
    tasks_disabled = [t.name for t in delta_disabled.task_queue]
    
    assert "node:js_node" not in tasks_disabled
    assert "node:api_node" not in tasks_disabled
    assert "node:passive_recon_node" in tasks_disabled
    assert "node:vulnerability_node" in tasks_disabled
    
    # 3. Determinism test
    delta1 = plan(state, config)
    delta2 = plan(state, config)
    assert delta1.model_dump() == delta2.model_dump()
