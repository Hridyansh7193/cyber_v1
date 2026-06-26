from abc import ABC, abstractmethod
from typing import Tuple, Any, Mapping
from pydantic import BaseModel, ConfigDict

class PluginMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    version: str
    description: str
    capabilities: Tuple[str, ...]
    supported_tools: Tuple[str, ...]

class PluginValidator(ABC):
    @abstractmethod
    def validate(self, target: Any, config: Mapping[str, Any]) -> bool:
        pass

class PluginParser(ABC):
    @abstractmethod
    def parse(self, stdout: str, stderr: str) -> Any:
        pass

class PluginRunner(ABC):
    @abstractmethod
    def build_command(self, target: Any, config: Mapping[str, Any]) -> Tuple[str, ...]:
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        pass

class ExecutionPlugin(PluginValidator, PluginParser, PluginRunner, ABC):
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass
