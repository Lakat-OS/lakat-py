import cbor2

def serialize(data):
    return cbor2.dumps(data)

def unserialize(data):
    return cbor2.loads(data)