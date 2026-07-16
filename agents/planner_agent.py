from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.task import Task, TaskPriority
from agents.deltas import TaskQueueDelta

# ---------------------------------------------------------------------------
# Canonical plugin prefix constants — must match ExecutionCoordinator._CAPABILITY_PREFIX
# ---------------------------------------------------------------------------
_PREFIX_PASSIVE_RECON = "plugin:passive_recon:"
_PREFIX_ACTIVE_RECON  = "plugin:active_recon:"
_PREFIX_JS            = "plugin:js:"
_PREFIX_API           = "plugin:api:"
_PREFIX_VULN          = "plugin:vuln:"
_PREFIX_PARAMETER     = "plugin:parameter:"


def plan(state: ExecutionState, config: BugHunterConfig) -> TaskQueueDelta:
    tasks = []
    
    # 1. Node Tasks (these drive the graph transition guards in each node)
    tasks.append(Task(name="node:passive_recon_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:scope_enforcement_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:active_recon_node", priority=TaskPriority.HIGH))
    
    # JS node
    if config.tools.enable_flags.get("js", True):
        tasks.append(Task(name="node:js_node", priority=TaskPriority.MEDIUM))
        
    # API node
    if config.tools.enable_flags.get("api", True):
        tasks.append(Task(name="node:api_node", priority=TaskPriority.MEDIUM))
        
    # Vuln, Parameter, Analysis, Report nodes
    tasks.append(Task(name="node:parameter_node", priority=TaskPriority.MEDIUM))
    tasks.append(Task(name="node:vulnerability_node", priority=TaskPriority.MEDIUM))
    tasks.append(Task(name="node:analysis_node", priority=TaskPriority.HIGH))
    tasks.append(Task(name="node:report_node", priority=TaskPriority.HIGH))
    
    # 2. Plugin Tasks — split into passive vs active so each stage runs the right tools.
    #
    # Passive recon: DNS/enumeration tools that don't probe the target actively.
    passive_recon_plugins = ["subfinder", "assetfinder", "gau"]
    #
    # Active recon: tools that actively connect to the target (crawlers, HTTP probers).
    active_recon_plugins = ["httpx", "katana"]
    
    js_plugins    = ["linkfinder", "secretfinder", "trufflehog"]
    api_plugins   = ["swagger", "graphql"]
    parameter_plugins = ["arjun"]
    vuln_plugins  = ["nuclei", "dalfox", "subzy", "ffuf"]
    
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
        
    for p in passive_recon_plugins: tasks.append(Task(name=f"{_PREFIX_PASSIVE_RECON}{p}"))
    for p in active_recon_plugins:  tasks.append(Task(name=f"{_PREFIX_ACTIVE_RECON}{p}"))
    for p in js_plugins:  tasks.append(Task(name=f"{_PREFIX_JS}{p}"))
    for p in api_plugins: tasks.append(Task(name=f"{_PREFIX_API}{p}"))
    for p in parameter_plugins: tasks.append(Task(name=f"{_PREFIX_PARAMETER}{p}"))
    for p in vuln_plugins: tasks.append(Task(name=f"{_PREFIX_VULN}{p}"))
    
    return TaskQueueDelta(task_queue=tuple(tasks))
