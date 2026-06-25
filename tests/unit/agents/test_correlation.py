from schemas.state import ExecutionState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from schemas.target import TargetState
from schemas.finding import Finding
from agents.correlation_agent import correlate
import uuid
from datetime import datetime, timezone

def test_correlation_agent():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    
    finding1 = Finding(
        title="XSS in http://test.com/search",
        severity="high",
        confidence="certain",
        evidence="evidence1"
    )
    
    finding2 = Finding(
        title="XSS in http://test.com/search",
        severity="high",
        confidence="certain",
        evidence="evidence2"
    )
    
    finding3 = Finding(
        title="SQLi in http://test.com/login",
        severity="critical",
        confidence="certain",
        evidence="evidence3"
    )
    
    state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)), findings=(finding1, finding2, finding3))
    
    correlated = correlate(state, config)
    
    assert len(correlated) == 2
    
    xss_group = [c for c in correlated if c.vulnerability_class == "XSS"][0]
    assert "evidence1" in xss_group.evidence
    assert "evidence2" in xss_group.evidence
    assert "http://test.com/search" in xss_group.affected_assets
    
    # Determinism test
    corr1 = correlate(state, config)
    corr2 = correlate(state, config)
    assert [c.model_dump() for c in corr1] == [c.model_dump() for c in corr2]
