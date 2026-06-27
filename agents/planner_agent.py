from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.planner_decision import PlannerDecision, ExecutionPlan
from schemas.intelligence import IntelligenceState
from agents.deltas.intelligence_delta import IntelligenceDelta

def plan(state: ExecutionState, config: BugHunterConfig) -> IntelligenceDelta:
    execute_nodes = []
    skipped_nodes = []
    reasoning = []
    
    # Simple logic to determine which plugins to run based on config.
    # In a real scenario, this would consult the profile and target state.
    recon_plugins = ("subfinder", "httpx", "assetfinder", "gau")
    js_plugins = ("linkfinder", "secretfinder", "trufflehog")
    api_plugins = ("swagger", "graphql")
    vuln_plugins = ("nuclei", "dalfox", "subzy", "ffuf")
    
    # 1. Recon is always executed unless we already have targets
    if not state.recon_state.subdomains and not state.recon_state.urls:
        execute_nodes.append("recon_node")
        reasoning.append("No existing recon data, executing recon_node.")
    else:
        execute_nodes.append("recon_node")
        reasoning.append("Executing recon_node to find more targets.")
        
    # 2. JS node
    if config.tools.enable_flags.get("js", True):
        execute_nodes.append("js_node")
    else:
        skipped_nodes.append("js_node")
        js_plugins = ()
        reasoning.append("JS module disabled by config.")
        
    # 3. API node
    if config.tools.enable_flags.get("api", True):
        execute_nodes.append("api_node")
    else:
        skipped_nodes.append("api_node")
        api_plugins = ()
        reasoning.append("API module disabled by config.")
        
    # 4. Vuln node
    execute_nodes.append("vulnerability_node")
    
    plan = ExecutionPlan(
        recon_plugins=recon_plugins,
        js_plugins=js_plugins,
        api_plugins=api_plugins,
        vuln_plugins=vuln_plugins
    )
    
    decision = PlannerDecision(
        execute_nodes=tuple(execute_nodes),
        skipped_nodes=tuple(skipped_nodes),
        execution_plan=plan,
        priority_overrides=(),
        reasoning=" ".join(reasoning),
        confidence=1.0
    )
    
    intelligence = IntelligenceState(planner=decision)
    return IntelligenceDelta(intelligence=intelligence)
