from datetime import datetime, timezone

from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.finding import Finding
from schemas.intelligence import IntelligenceState
from schemas.attack_graph import AttackGraph, AttackGraphNode
from schemas.risk_summary import RiskSummary
from config.schemas import BugHunterConfig, SettingsConfig, ReportingConfig

from agents.reporter_agent import generate_reports
from reporting.markdown_renderer import generate_markdown

def test_report_includes_intelligence(tmp_path):
    from config.schemas import LLMConfig, ToolsConfig, TimeoutsConfig
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=10, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4o", timeout=60, OPENAI_API_KEY="test"),
        tools=ToolsConfig(
            tool_paths={"subfinder": "subfinder"},
            docker_container_names={},
            wordlists={},
            enable_flags={}
        ),
        timeouts=TimeoutsConfig(subfinder_timeout=60, nuclei_timeout=300, dalfox_timeout=300, ffuf_timeout=300, global_timeout=3600),
        reporting=ReportingConfig(
            report_formats=["markdown", "json"],
            output_directories={
                "markdown": str(tmp_path / "md"),
                "json": str(tmp_path / "json")
            }
        )
    )
    
    # Execution State WITH Intelligence
    ag = AttackGraph(
        nodes=(AttackGraphNode(id="root", type="TARGET", label="Target"),),
        edges=(),
        confidence=1.0
    )
    
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test-123", start_time=datetime.now(timezone.utc)),
        findings=(
            Finding(title="SQLi", severity="high", confidence="high", evidence=""),
        ),
        intelligence=IntelligenceState(
            version=1,
            attack_graph=ag,
            risk_summary=RiskSummary(score=8.5, level="HIGH", reasoning="SQLi found")
        )
    )
    
    # Generate report
    delta = generate_reports(state, config)
    report = generate_markdown(delta.reports[0])
    
    # The report should contain the intelligence data
    assert "Intelligence" in report.content or "Risk Summary" in report.content or "Attack Graph" in report.content
    
    # Verify the fallback state (no intelligence) doesn't break
    state_no_intel = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test-123", start_time=datetime.now(timezone.utc)),
        findings=(
            Finding(title="SQLi", severity="high", confidence="high", evidence=""),
        ),
    )
    
    delta2 = generate_reports(state_no_intel, config)
    report2 = generate_markdown(delta2.reports[0])
    
    # It shouldn't contain the intel sections but should render fine
    assert report2.content
