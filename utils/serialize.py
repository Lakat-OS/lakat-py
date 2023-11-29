from ipld import marshal, unmarshal
import rlp
import json
import base64

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
    

def custom_json_decoder(obj):
    """
    Custom decoder function for JSON objects.
    Converts Base64 encoded strings back into bytes.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                try:
                    obj[key] = base64.b64decode(value)
                except (ValueError, TypeError):
                    pass
    return obj


class Serializer:
    
    def serialize(o) -> bytes :
        return marshal(o)

    def deserialize(data: bytes) -> any :
        return unmarshal(data)
    

def serialize(obj):
    """
    Serialize a Python object into bytes.
    
    :param obj: Python object to serialize.
    :return: Bytes representation of the object.
    """
    json_string = json.dumps(obj, cls=BytesEncoder)
    return json_string.encode('utf-8')

def unserialize(bytes_obj):
    """
    Unserialize bytes back into a Python object.
    
    :param bytes_obj: Bytes object to unserialize.
    :return: Original Python object.
    """
    return json.loads(bytes_obj.decode('utf-8'), object_hook=custom_json_decoder)


def jsondump(obj, file):
    json.dump(obj, file, cls=BytesEncoder, indent=2)


def jsonload(file):
    return json.load(file, object_hook=custom_json_decoder)



def serialize_with_rlp(obj):
    """
    Recursively serialize a Python object using RLP.
    """
    if isinstance(obj, dict):
        return {k: serialize_with_rlp(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_with_rlp(item) for item in obj]
    elif isinstance(obj, bytes):
        return obj
    else:
        return str(obj).encode()

def unserialize_with_rlp(encoded_obj):
    """
    Recursively unserialize an object encoded with RLP.
    """
    if isinstance(encoded_obj, bytes):
        try:
            decoded = rlp.decode(encoded_obj)
            if isinstance(decoded, list):
                return [unserialize_with_rlp(item) for item in decoded]
            return decoded
        except Exception:
            return encoded_obj
    elif isinstance(encoded_obj, list):
        return [unserialize_with_rlp(item) for item in encoded_obj]
    else:
        return encoded_obj

# # Example usage
# example_object = {"key": [b'data', 123, 'string']}
# serialized = rlp.encode(serialize_with_rlp(example_object))
# print("RLP Serialized:", serialized)

# unserialized = unserialize_with_rlp(serialized)
# print("RLP Unserialized:", unserialized)
