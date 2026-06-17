from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Mapping, Tuple, Any
from types import MappingProxyType

class TestModel(BaseModel):
    model_config = ConfigDict(frozen=True)
    metadata: Mapping[str, Any] = Field(default_factory=lambda: MappingProxyType({}))
    items: Tuple[str, ...] = Field(default=())

    @field_serializer('metadata')
    def serialize_metadata(self, v: Mapping[str, Any], _info):
        return dict(v)

obj = TestModel()
print(obj.model_dump_json())
