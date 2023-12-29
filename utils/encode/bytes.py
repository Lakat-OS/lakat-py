import base64
import base58
from config.db_cfg import HASH_ENCODING_STYLE

def encode_bytes_to_base64_str(bytes_data: bytes):
    return base64.b64encode(bytes_data).decode('utf-8')

def decode_base64_str_to_bytes(base64_str: str):
    return base64.b64decode(base64_str.encode('utf-8'))

def encode_bytes_to_base58_str(bytes_data: bytes):
    return base58.b58encode(bytes_data).decode('utf-8')

def decode_base58_str_to_bytes(base58_str: str):
    return base58.b58decode(base58_str.encode('utf-8'))


if HASH_ENCODING_STYLE == "base58":
    key_encoder = encode_bytes_to_base58_str
elif HASH_ENCODING_STYLE == "base64":
    key_encoder = encode_bytes_to_base64_str
else:
    raise Exception("Unsupported encoding style: " + HASH_ENCODING_STYLE)