import time
from typing import Callable, Any, Tuple
from config.schemas import BugHunterConfig
from schemas.state import ExecutionState
from schemas.tool_result import ToolResult
from schemas.runtime import Capability
from orchestrator.execution_coordinator import ExecutionCoordinator
from utils.logger import get_logger

logger = get_logger("node_executor")

def execute_node(
    current_exec: ExecutionState,
    config: BugHunterConfig,
    capability: Capability = None,
    wrapper_func: Callable[[Tuple[str, ...], BugHunterConfig, ExecutionState], Tuple[ToolResult, ...]] = None,
    wrapper_applier: Callable[[Any, Any], Any] = None,
    agent: Callable[[Any, Any], Any] = None,
    delta_applier: Callable[[Any, Any], Any] = None
) -> ExecutionState:
    # 1. Wrapper — run tool plugins
    if capability and wrapper_func and wrapper_applier:
        t0 = time.monotonic()
        logger.debug(f"execute_node: running wrapper for capability={capability}")
        wrapper_out = ExecutionCoordinator.execute_capability(current_exec, config, capability, wrapper_func)
        elapsed = time.monotonic() - t0
        logger.debug(f"execute_node: wrapper done ({len(wrapper_out)} results) in {elapsed:.2f}s")
        current_exec = wrapper_applier(current_exec, wrapper_out)
        
    # 2. Agent — LLM/rule-based delta computation
    if agent and delta_applier:
        t0 = time.monotonic()
        agent_name = getattr(agent, "__name__", str(agent))
        logger.debug(f"execute_node: running agent={agent_name}")
        delta = agent(current_exec, config)
        elapsed = time.monotonic() - t0
        logger.debug(f"execute_node: agent={agent_name} done in {elapsed:.2f}s")
        current_exec = delta_applier(current_exec, delta)
        
    return current_exec
