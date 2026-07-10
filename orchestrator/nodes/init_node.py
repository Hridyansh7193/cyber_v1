from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.queue_manager import update_task_status
from schemas.errors import ConfigurationError, ErrorCode
from runtime.workspace import WorkspaceManager
import os

def init_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    # Phase 5: Fast-Fail Configuration Validation
    ws_manager = WorkspaceManager()
    base_dir = ws_manager.root_dir
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Workspace / Output Directory Writability
    if not os.access(base_dir, os.W_OK):
        raise ConfigurationError(
            ErrorCode.WORKSPACE_UNWRITABLE, 
            f"Workspace directory is not writable: {base_dir}"
        )

    # 2. Database writability / lock check
    db_path = os.path.join(base_dir, "bughunter.db")
    if os.path.exists(db_path) and not os.access(db_path, os.W_OK):
        raise ConfigurationError(
            ErrorCode.DB_LOCK_TIMEOUT, 
            f"Database file is not writable (could be locked): {db_path}"
        )
        
    # 3. Check for API keys if we plan to use plugins that require them
    # For now, we assume if dalfox or similar requires an API key, it fails fast in doctor. 
    # But for BugHunter config, maybe LLM requires an API key.
    if config.llm.provider != "dummy" and not getattr(config.llm, f"{config.llm.provider.upper()}_API_KEY", None):
        pass # Optional: LLM validation can go here if LLM is actually enabled
        
    new_orch = update_task_status(state.orchestration_state, "init", "COMPLETED")
    return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)
