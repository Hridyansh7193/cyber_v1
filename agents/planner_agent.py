from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.task import Task, TaskPriority
from agents.deltas import TaskQueueDelta

def plan(state: ExecutionState, config: BugHunterConfig) -> TaskQueueDelta:
    tasks = []
    
    # 1. Node Tasks
    # Recon is always executed unless we already have targets
    tasks.append(Task(name="node:passive_recon_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:active_recon_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:scope_enforcement_node", priority=TaskPriority.HIGH))
    
    # JS node
    if config.tools.enable_flags.get("js", True):
        tasks.append(Task(name="node:js_node", priority=TaskPriority.MEDIUM))
        
    # API node
    if config.tools.enable_flags.get("api", True):
        tasks.append(Task(name="node:api_node", priority=TaskPriority.MEDIUM))
        
    # Vuln node
    tasks.append(Task(name="node:vulnerability_node", priority=TaskPriority.MEDIUM))
    
    # Parameter, Analysis, and Report nodes
    tasks.append(Task(name="node:parameter_node", priority=TaskPriority.MEDIUM))
    tasks.append(Task(name="node:analysis_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:report_node", priority=TaskPriority.HIGH))
    
    # 2. Plugin Tasks
    recon_plugins = ["subfinder", "httpx", "assetfinder", "katana", "gau"]
    js_plugins = ["linkfinder", "secretfinder", "trufflehog"]
    api_plugins = ["swagger", "graphql"]
    vuln_plugins = ["nuclei", "dalfox", "subzy", "ffuf"]
    
    has_waf = any(state.recon_state.waf_detected.values())
    if has_waf:
        if "dalfox" in vuln_plugins: vuln_plugins.remove("dalfox")
        if "ffuf" in vuln_plugins: vuln_plugins.remove("ffuf")
            
    is_wordpress = any("wordpress" in str(techs).lower() for techs in state.recon_state.tech_stack.values())
    if is_wordpress and "wpscan" not in vuln_plugins:
        vuln_plugins.append("wpscan")
        
    if state.api_state.swagger_urls or state.api_state.graphql_urls or state.api_state.endpoints:
        if "graphql" not in api_plugins: api_plugins.append("graphql")
        if "swagger" not in api_plugins: api_plugins.append("swagger")
        
    # If the user disabled js/api nodes, don't schedule their plugins
    if not config.tools.enable_flags.get("js", True):
        js_plugins = []
    if not config.tools.enable_flags.get("api", True):
        api_plugins = []
        
    for p in recon_plugins: tasks.append(Task(name=f"plugin:recon:{p}"))
    for p in js_plugins: tasks.append(Task(name=f"plugin:js:{p}"))
    for p in api_plugins: tasks.append(Task(name=f"plugin:api:{p}"))
    for p in vuln_plugins: tasks.append(Task(name=f"plugin:vuln:{p}"))
    
    return TaskQueueDelta(task_queue=tuple(tasks))
