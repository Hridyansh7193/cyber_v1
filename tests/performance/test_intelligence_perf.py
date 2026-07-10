import time
from datetime import datetime, timezone
from schemas.state import ExecutionState, ReconState, TargetState
from schemas.finding import Finding
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from agents.planner_agent import plan
from agents.correlation_agent import correlate
from agents.attack_graph_agent import generate_graph

def create_large_state():
    findings = []
    # 10,000 findings
    for i in range(10000):
        findings.append(Finding(
            title=f"XSS in http://sub{i % 100}.example.com/api/v1/user{i}",
            severity="high",
            confidence="certain",
            evidence="evidence_payload"
        ))
        
    recon_state = ReconState(
        subdomains=[f"sub{i}.example.com" for i in range(100)],
        urls=[f"http://sub{i % 100}.example.com/api/v1/user{i}" for i in range(10000)]
    )
    
    return ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)),
        recon_state=recon_state,
        findings=tuple(findings)
    )

def test_intelligence_performance():
    config = BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )
    state = create_large_state()
    
    # 1. Planner (< 50ms)
    start = time.perf_counter()
    plan(state, config)
    duration_planner = (time.perf_counter() - start) * 1000
    assert duration_planner < 50, f"Planner too slow: {duration_planner:.2f}ms"
    
    # 2. Correlation (< 500ms)
    start = time.perf_counter()
    correlate(state, config)
    duration_correlation = (time.perf_counter() - start) * 1000
    assert duration_correlation < 500, f"Correlation too slow: {duration_correlation:.2f}ms"
    
    # 3. Attack Graph (< 1s)
    start = time.perf_counter()
    generate_graph(state, config)
    duration_graph = (time.perf_counter() - start) * 1000
    assert duration_graph < 1000, f"Attack graph too slow: {duration_graph:.2f}ms"
    
    print(f"\nPerformance: Planner={duration_planner:.2f}ms, Correlation={duration_correlation:.2f}ms, Graph={duration_graph:.2f}ms")
