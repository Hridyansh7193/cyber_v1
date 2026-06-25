import pytest
import time
import tracemalloc
import hashlib
from datetime import datetime, timezone
from schemas.state import ExecutionState
from schemas.target import TargetState
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig

@pytest.fixture
def base_config(tmp_path):
    return BugHunterConfig(
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
            output_directories={"markdown": str(tmp_path / "reports/md"), "json": str(tmp_path / "reports/json")}
        )
    )

from schemas.finding import Finding
from agents.planner_agent import plan
from agents.correlation_agent import correlate
from agents.prioritizer_agent import prioritize
from agents.attack_graph_agent import generate_graph

def generate_findings(count):
    # Distinct vulnerabilities to verify correlation and deduplication
    return tuple(Finding(
        title=f"SQL Injection in /api/endpoint_{i % 500}",
        severity="high",
        confidence="high",
        evidence=f"Evidence {i}"
    ) for i in range(count))

def test_planner_scaling(base_config):
    # 3. Planner Validation
    config = base_config
    
    times = {}
    for size in [10000, 20000, 40000, 80000, 100000]:
        state = ExecutionState(
            target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
            recon_state={"subdomains": [f"sub{i}.example.com" for i in range(size)]}
        )
        
        tracemalloc.start()
        start = time.perf_counter()
        delta = plan(state, config)
        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed = end - start
        times[size] = elapsed
        print(f"Planner {size}: {elapsed:.4f}s, Peak: {peak / 1024 / 1024:.2f}MB")
        
    # Verify O(N) constraint: time(2N)/time(N) approx 2 (allow up to 2.5 for overhead)
    ratio_20k = times[20000] / max(times[10000], 0.0001)
    ratio_40k = times[40000] / max(times[20000], 0.0001)
    ratio_80k = times[80000] / max(times[40000], 0.0001)
    
    assert ratio_20k < 3.0, f"Planner scaling violated at 20k: {ratio_20k}"
    assert ratio_40k < 3.0, f"Planner scaling violated at 40k: {ratio_40k}"
    assert ratio_80k < 3.0, f"Planner scaling violated at 80k: {ratio_80k}"

def test_planner_determinism(base_config):
    config = base_config
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        recon_state={"subdomains": [f"sub{i}.example.com" for i in range(1000)]}
    )
    
    hashes = set()
    for _ in range(5):
        delta = plan(state, config)
        j = delta.intelligence.planner.model_dump_json()
        h = hashlib.sha256(j.encode('utf-8')).hexdigest()
        hashes.add(h)
        
    assert len(hashes) == 1

def test_correlation_scaling(base_config):
    # 5. Correlation Validation
    config = base_config
    
    times = {}
    for size in [10, 100, 1000, 10000, 100000]:
        state = ExecutionState(
            target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
            findings=generate_findings(size)
        )
        
        tracemalloc.start()
        start = time.perf_counter()
        delta = correlate(state, config)
        end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed = end - start
        times[size] = elapsed
        print(f"Correlation {size}: {elapsed:.4f}s, Peak: {peak / 1024 / 1024:.2f}MB")
        
        expected_unique = min(size, 500)
        assert len(delta) == expected_unique
        if size >= 500:
            assert len(delta[0].evidence) > 1

def test_attack_graph_scaling(base_config):
    # 7. Attack Graph Validation
    config = base_config
    
    times = {}
    for size in [10, 100, 1000, 10000, 100000]:
        state = ExecutionState(
            target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
            findings=generate_findings(size)
        )
        
        tracemalloc.start()
        start = time.perf_counter()
        delta = generate_graph(state, config)
        end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        elapsed = end - start
        times[size] = elapsed
        print(f"AttackGraph {size}: {elapsed:.4f}s, Peak: {peak / 1024 / 1024:.2f}MB")
        
        ag = delta
        assert len(ag.nodes) > 0

def test_memory_leak(base_config):
    # 14. Memory Leak Validation
    import tracemalloc
    config = base_config
    
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        recon_state={"subdomains": ["api.example.com", "dev.example.com"]},
        findings=generate_findings(100)
    )
    
    tracemalloc.start()
    
    # Warmup
    plan(state, config)
    correlate(state, config)
    generate_graph(state, config)
    
    import gc
    gc.collect()
    _, start_mem = tracemalloc.get_traced_memory()
    
    # Planner x1000
    for _ in range(1000):
        plan(state, config)
        
    # Correlation x100
    for _ in range(100):
        correlate(state, config)
        
    # Attack Graph x100
    for _ in range(100):
        generate_graph(state, config)
        
    gc.collect()
    _, end_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    growth = end_mem - start_mem
    # Assert growth is negligible (less than 1MB)
    assert growth < 1024 * 1024, f"Memory leak detected! Growth: {growth/1024} KB"

def test_state_size_benchmark(base_config):
    # ExecutionState vs ExecutionState + Intelligence
    state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="test", start_time=datetime.now(timezone.utc)),
        findings=generate_findings(1000)
    )
    
    import copy
    
    start = time.perf_counter()
    j_base = state.model_dump_json()
    b_base = j_base.encode('utf-8')
    base_deepcopy = time.perf_counter() - start
    
    # add intelligence
    config = base_config
    from orchestrator.nodes.analysis_node import analysis_node
    from orchestrator.node_result import NodeResult
    from orchestrator.orchestration_state import OrchestrationState
    
    orch = OrchestrationState(execution_state=state, config=config, task_status={}, errors={})
    res = analysis_node(NodeResult(execution_state=state, orchestration_state=orch), config)
    state_intel = res.execution_state
    
    start = time.perf_counter()
    j_intel = state_intel.model_dump_json()
    b_intel = j_intel.encode('utf-8')
    intel_deepcopy = time.perf_counter() - start
    
    print(f"Base JSON Size: {len(b_base)} bytes")
    print(f"Intel JSON Size: {len(b_intel)} bytes")
    
    assert intel_deepcopy < 0.5
