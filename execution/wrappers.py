from typing import Tuple
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugin_executor import PluginExecutor

class ReconWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target, result_key="new_subdomains")

class JSWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target, result_key="new_endpoints")

class APIWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target, result_key="new_swagger")

class VulnWrapper:
    @staticmethod
    def execute(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: str) -> Tuple[ToolResult, ...]:
        return PluginExecutor.execute_plugins(plugin_names, config, target, result_key="new_nuclei")
