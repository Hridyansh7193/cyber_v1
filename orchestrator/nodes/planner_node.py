from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from agents.planner_agent import plan
from orchestrator.delta_applier import apply_intelligence_delta
from orchestrator.queue_manager import start_task, complete_task
from orchestrator.node_executor import execute_node

def planner_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    orch = start_task(state.orchestration_state, "planner")
    
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        agent=plan,
        delta_applier=apply_intelligence_delta
    )
    
    orch = complete_task(orch, "planner")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
