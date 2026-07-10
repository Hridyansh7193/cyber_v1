import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.finding import Finding
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig

from agents.planner_agent import plan
from agents.prioritizer_agent import prioritize
from agents.risk_score_agent import score_risk
from agents.deltas.intelligence_delta import IntelligenceDelta
from schemas.intelligence import IntelligenceState
from orchestrator.delta_applier import apply_intelligence_delta

@pytest.fixture
def base_config(tmp_path):
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=10, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4o", timeout=60, OPENAI_API_KEY="test"),
        tools=ToolsConfig(
            tool_paths={"subfinder": "subfinder"},
            docker_container_names={},
            wordlists={},
            enable_flags={"js": False, "api": True} # Test disabling JS
        ),
        timeouts=TimeoutsConfig(subfinder_timeout=60, nuclei_timeout=300, dalfox_timeout=300, ffuf_timeout=300, global_timeout=3600),
        reporting=ReportingConfig(
            report_formats=["markdown", "json"],
            output_directories={"markdown": str(tmp_path / "reports/md"), "json": str(tmp_path / "reports/json")}
        )
    )

def test_planner_effectiveness(base_config):
    # 4. Planner Effectiveness Validation
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        recon_state={"subdomains": ["api.example.com"]}
    )
    
    delta = plan(state, base_config)
    tasks = [t.name for t in delta.task_queue]
    
    # Recon and API should be included
    assert "node:passive_recon_node" in tasks
    assert "node:api_node" in tasks

def test_prioritizer_validation(base_config):
    # 6. Prioritizer Validation
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        recon_state={"urls": ["https://admin.example.com"]}
    )

    delta = prioritize(state, base_config)

    assert len(delta) > 0

def test_risk_summary_validation(base_config):
    # 8. Risk Summary Validation
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        findings=[
            Finding(title="SQLi", severity="high", confidence="high", evidence=""),
            Finding(title="Info Disclosure", severity="low", confidence="high", evidence="")
        ]
    )
    
    delta = score_risk(state, base_config)
    
    assert delta.score > 0
    assert delta.level == "HIGH"

def test_intelligence_delta_applier():
    # 9. Intelligence Delta Validation
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
    )
    
    # Empty intelligence
    assert state.intelligence is None
    
    # First delta
    from schemas.prioritized_asset import PrioritizedAsset
    p_asset = PrioritizedAsset(asset="https://api.example.com", asset_type="URL", score=10.0, reasoning="API")
    delta1 = IntelligenceDelta(intelligence=IntelligenceState(version=1, planner=None, prioritized_assets=(p_asset,)))
    state2 = apply_intelligence_delta(state, delta1)
    assert state2.intelligence.prioritized_assets[0].asset == "https://api.example.com"
    
    # Second delta updates only risk summary
    from schemas.risk_summary import RiskSummary
    delta2 = IntelligenceDelta(intelligence=IntelligenceState(version=2, risk_summary=RiskSummary(score=8.5, level="HIGH", reasoning="")))
    state3 = apply_intelligence_delta(state2, delta2)
    
    # Must merge, not replace!
    assert state3.intelligence.prioritized_assets[0].asset == "https://api.example.com"
    assert state3.intelligence.risk_summary.score == 8.5

def test_architecture_isolation_frozen_state(base_config):
    # 10. Architecture Isolation (Frozen State)
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        findings=(Finding(title="SQLi", severity="high", confidence="high", evidence=""),)
    )
    
    with pytest.raises(Exception):
        # Should raise TypeError because tuples are immutable
        state.findings.append(Finding(title="XSS", severity="low", confidence="high", evidence=""))
        
    with pytest.raises(Exception):
        # Should raise ValidationError or TypeError because state is frozen
        state.findings = ()
