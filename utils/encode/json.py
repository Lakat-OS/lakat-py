import json 
from utils.encode.bytes import key_encoder


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return key_encoder(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
    

def jsondump(obj, file):
    json.dump(obj, file, cls=BytesEncoder, indent=2)