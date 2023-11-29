from ipld import multihash
from serialize import serializer

def _serializeAndMultihash(obj):                            
    serialized = serializer.serialize(obj)
    return serialized, multihash(serialized)