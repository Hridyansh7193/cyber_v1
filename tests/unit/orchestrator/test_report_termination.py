import pytest
from orchestrator.graph import build_graph
from orchestrator.checkpoint_manager import CheckpointManager
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig

@pytest.fixture
def mock_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )

def test_report_terminates_graph(mock_config):
    manager = CheckpointManager()
    graph = build_graph(mock_config, checkpointer=manager)
    
    # In langgraph, edges are stored in builder
    # The edge from report_node must go to END
    # We can check transitions.py or graph edges
    edges = graph.builder.edges
    assert ("report_node", "__end__") in edges or any(edge[0] == "report_node" and edge[1] == "__end__" for edge in edges)
