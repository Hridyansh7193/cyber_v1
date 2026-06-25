from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.queue_manager import start_task, complete_task
from agents.planner_agent import plan
from orchestrator.delta_applier import apply_intelligence_delta

def planner_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    orch = start_task(state.orchestration_state, "planner")
    
    # Run the planner agent
    delta = plan(state.execution_state, config)
    
    # Apply intelligence delta
    new_exec = apply_intelligence_delta(state.execution_state, delta)
    
    orch = complete_task(orch, "planner")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
