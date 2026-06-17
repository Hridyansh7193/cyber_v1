from pydantic import BaseModel, ConfigDict, Field
from typing import Mapping, Tuple, Any
from types import MappingProxyType

class TestModel(BaseModel):
    model_config = ConfigDict(frozen=True)
    metadata: Mapping[str, Any] = Field(default_factory=lambda: MappingProxyType({}))
    items: Tuple[str, ...] = Field(default=())

obj = TestModel()
try:
    obj.metadata["key"] = "value"
    print("MUTABLE DICT")
except Exception as e:
    print("FROZEN DICT", type(e))

try:
    obj.items += ("new",)
    print("MUTABLE TUPLE")
except Exception as e:
    print("FROZEN TUPLE", type(e))
