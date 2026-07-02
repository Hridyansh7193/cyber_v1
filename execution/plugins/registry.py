from typing import Dict, Optional, Tuple, List
from pydantic import BaseModel, ConfigDict
from .base import ExecutionPlugin

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, ExecutionPlugin] = {}
        
    def register(self, name: str, plugin: ExecutionPlugin) -> None:
        self._plugins[name] = plugin
        
    def get_plugin(self, name: str) -> Optional[ExecutionPlugin]:
        return self._plugins.get(name)
        
    def list_plugins(self) -> Tuple[str, ...]:
        return tuple(self._plugins.keys())

# Global registry instance
REGISTRY = PluginRegistry()

# Initialize registry with static imports (no dynamic imports allowed)
from execution.recon.subfinder_wrapper import SubfinderWrapper
from execution.recon.httpx_wrapper import HttpxPlugin
from execution.recon.katana_wrapper import KatanaPlugin
from execution.recon.assetfinder_wrapper import AssetfinderWrapper
from execution.recon.gau_wrapper import GauWrapper
from execution.js.linkfinder_wrapper import LinkFinderWrapper
from execution.js.secretfinder_wrapper import SecretFinderWrapper
from execution.vuln.nuclei_wrapper import NucleiPlugin
from execution.vuln.dalfox_wrapper import DalfoxPlugin
from execution.api.swagger_wrapper import SwaggerPlugin
from execution.api.graphql_wrapper import GraphQLPlugin
from execution.js.trufflehog_wrapper import TrufflehogWrapper
from execution.vuln.ffuf_wrapper import FfufPlugin
from execution.vuln.subzy_wrapper import SubzyPlugin

from execution.discovery.arjun_wrapper import ArjunPlugin

REGISTRY.register("subfinder", SubfinderWrapper())
REGISTRY.register("httpx", HttpxPlugin())
REGISTRY.register("katana", KatanaPlugin())
REGISTRY.register("assetfinder", AssetfinderWrapper())
REGISTRY.register("gau", GauWrapper())
REGISTRY.register("linkfinder", LinkFinderWrapper())
REGISTRY.register("secretfinder", SecretFinderWrapper())
REGISTRY.register("nuclei", NucleiPlugin())
REGISTRY.register("dalfox", DalfoxPlugin())
REGISTRY.register("swagger", SwaggerPlugin())
REGISTRY.register("graphql", GraphQLPlugin())
REGISTRY.register("trufflehog", TrufflehogWrapper())
REGISTRY.register("ffuf", FfufPlugin())
REGISTRY.register("subzy", SubzyPlugin())
REGISTRY.register("arjun", ArjunPlugin())
