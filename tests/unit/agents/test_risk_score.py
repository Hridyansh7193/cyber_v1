from schemas.state import ExecutionState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from schemas.target import TargetState
from schemas.finding import Finding
from agents.risk_score_agent import score_risk
import uuid
from datetime import datetime, timezone

def test_risk_score_agent():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    
    finding1 = Finding(
        title="XSS",
        severity="medium",
        confidence="certain",
        evidence=""
    )
    finding2 = Finding(
        title="SQLi",
        severity="critical",
        confidence="certain",
        evidence=""
    )
    
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)),
        findings=(finding1, finding2)
    )
    
    risk = score_risk(state, config)
    assert risk.score == 10.0
    assert risk.level == "CRITICAL"
    
    # Determinism
    risk1 = score_risk(state, config)
    risk2 = score_risk(state, config)
    assert risk1.model_dump() == risk2.model_dump()
