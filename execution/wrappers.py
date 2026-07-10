from typing import Tuple
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugin_executor import PluginExecutor
from schemas.state import ExecutionState

class ReconWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, state)

class JSWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, state)

class APIWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, state)

class VulnWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, state)

class ParameterWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, state)
