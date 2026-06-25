from schemas.state import ExecutionState, ReconState, APIState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from schemas.target import TargetState
from agents.prioritizer_agent import prioritize
from datetime import datetime, timezone

def test_prioritizer_agent():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    
    recon_state = ReconState(
        urls=("http://example.com/login", "http://example.com/api/v1/users", "http://example.com/about")
    )
    api_state = APIState(
        swagger_urls=("http://example.com/api/docs",),
        graphql_urls=()
    )
    
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)),
        recon_state=recon_state,
        api_state=api_state
    )
    
    assets = prioritize(state, config)
    
    assert len(assets) == 4
    # Swagger should be 50.0
    assert assets[0].asset_type == "SWAGGER"
    assert assets[0].score == 50.0
    # Login should be 30.0 (10 + 20)
    assert assets[1].asset == "http://example.com/login"
    assert assets[1].score == 30.0
    # API should be 25.0 (10 + 15)
    assert assets[2].asset == "http://example.com/api/v1/users"
    assert assets[2].score == 25.0
    # About should be 10.0
    assert assets[3].asset == "http://example.com/about"
    assert assets[3].score == 10.0
    
    # Determinism
    assets1 = prioritize(state, config)
    assets2 = prioritize(state, config)
    assert [a.model_dump() for a in assets1] == [a.model_dump() for a in assets2]
