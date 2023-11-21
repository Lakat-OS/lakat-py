from ipld import marshal, multihash, unmarshal

class Serializer:
    
    def serialize(o) -> bytes :
        return marshal(o)

    def deserialize(data: bytes) -> any :
        return unmarshal(data)
    