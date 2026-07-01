from typing import Tuple
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugin_executor import PluginExecutor

class ReconWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target)

class JSWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target)

class APIWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target)

class VulnWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target)
