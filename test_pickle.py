import copy
from types import MappingProxyType
import copyreg

def pickle_mappingproxy(proxy):
    return MappingProxyType, (dict(proxy),)

copyreg.pickle(MappingProxyType, pickle_mappingproxy)

d = MappingProxyType({"a": 1})
d2 = copy.deepcopy(d)
print(d2, type(d2))
