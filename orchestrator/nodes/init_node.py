from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.queue_manager import update_task_status
from schemas.errors import ConfigurationError, ErrorCode
from runtime.workspace import WorkspaceManager
from utils.logger import get_logger
import os

logger = get_logger("init_node")

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
        
    # 3. Warn if a real LLM provider is configured without an API key.
    #    This is a warning, not a hard fail — LLM is optional for most nodes.
    provider = config.llm.provider if config.llm else "dummy"
    if provider and provider != "dummy":
        api_key_attr = f"{provider.upper()}_API_KEY"
        api_key = getattr(config.llm, api_key_attr, None)
        if not api_key:
            logger.warning(
                f"LLM provider '{provider}' is configured but no API key found "
                f"(expected config.llm.{api_key_attr}). "
                f"LLM-dependent features will be skipped or may fail."
            )
        
    new_orch = update_task_status(state.orchestration_state, "init", "COMPLETED")
    return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)
