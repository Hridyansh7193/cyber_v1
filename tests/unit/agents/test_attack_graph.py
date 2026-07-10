from schemas.state import ExecutionState, ReconState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from schemas.target import TargetState
from schemas.finding import Finding
from agents.attack_graph_agent import generate_graph
from datetime import datetime, timezone

def test_attack_graph_agent():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    
    finding1 = Finding(
        title="XSS in http://sub.example.com/search",
        severity="high",
        confidence="certain",
        evidence=""
    )
    
    recon_state = ReconState(
        subdomains=("sub.example.com",),
        urls=("http://sub.example.com/search",)
    )
    
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)),
        recon_state=recon_state,
        findings=(finding1,)
    )
    
    graph = generate_graph(state, config)
    
    # We expect target_root -> sub_sub.example.com -> url_http://sub.example.com/search -> finding_XSS in http://sub.example.com/search
    # Check entry point
    assert "target_root" in graph.entry_points
    
    nodes = {n.id: n for n in graph.nodes}
    assert "target_root" in nodes
    assert "sub_sub.example.com" in nodes
    assert "url_http://sub.example.com/search" in nodes
    assert "finding_XSS in http://sub.example.com/search" in nodes
    
    edges = {(e.source, e.target) for e in graph.edges}
    assert ("target_root", "sub_sub.example.com") in edges
    assert ("sub_sub.example.com", "url_http://sub.example.com/search") in edges
    assert ("url_http://sub.example.com/search", "finding_XSS in http://sub.example.com/search") in edges
    
    # Determinism
    graph1 = generate_graph(state, config)
    graph2 = generate_graph(state, config)
    assert graph1.model_dump() == graph2.model_dump()
