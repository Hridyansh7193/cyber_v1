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
    recon_plugins = ("subfinder", "httpx", "assetfinder", "katana", "gau")
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
    
    # 5. WAF and Tech Stack Logic
    has_waf = any(state.recon_state.waf_detected.values())
    vuln_plugins_list = list(vuln_plugins)
    js_plugins_list = list(js_plugins)
    api_plugins_list = list(api_plugins)
    recon_plugins_list = list(recon_plugins)
    
    if has_waf:
        reasoning.append("WAF detected. Limiting aggressive tools (skipping Dalfox and ffuf).")
        if "dalfox" in vuln_plugins_list:
            vuln_plugins_list.remove("dalfox")
        if "ffuf" in vuln_plugins_list:
            vuln_plugins_list.remove("ffuf")
            
    is_wordpress = any("wordpress" in str(techs).lower() for techs in state.recon_state.tech_stack.values())
    if is_wordpress and "wpscan" not in vuln_plugins_list:
        reasoning.append("WordPress detected. Enabling WPScan.")
        vuln_plugins_list.append("wpscan")
        
    # 6. JavaScript Logic
    if not state.js_state.js_files and state.target.session_id: # Only skip if we've already done some recon and found none. If it's the first run, we might not have JS files yet, but wait, JS files are found by recon? No, gau/wayback finds them.
        # Actually, let's keep them if it's the first pass, but planner runs before execution.
        pass

    # 7. API Logic
    if state.api_state.swagger_urls or state.api_state.graphql_urls or state.api_state.endpoints:
        reasoning.append("APIs detected. Prioritizing API tools.")
        if "graphql" not in api_plugins_list:
            api_plugins_list.append("graphql")
        if "swagger" not in api_plugins_list:
            api_plugins_list.append("swagger")
            
    # Add parameter node plugins if needed (arjun is handled by orchestrator, but we can add it here if planner controls it)
    parameter_plugins = ("arjun",)
    
    plan = ExecutionPlan(
        recon_plugins=tuple(recon_plugins_list),
        js_plugins=tuple(js_plugins_list),
        api_plugins=tuple(api_plugins_list),
        vuln_plugins=tuple(vuln_plugins_list)
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
