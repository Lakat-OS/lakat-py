import base64
import base58
import binascii

from config.db_cfg import HASH_ENCODING_STYLE
from lakat.errors import ERR_N_ENC_1, ERR_T_ENC_1

def encode_bytes_to_base64_str(bytes_data: bytes):
    return base64.b64encode(bytes_data).decode('utf-8')

def decode_base64_str_to_bytes(base64_str: str):
    return base64.b64decode(base64_str.encode('utf-8'))

def encode_bytes_to_base58_str(bytes_data: bytes):
    return base58.b58encode(bytes_data).decode('utf-8')

def decode_base58_str_to_bytes(base58_str: str):
    return base58.b58decode(base58_str.encode('utf-8'))

def encode_bytes_to_hex_str(bytes_data: bytes):
    return binascii.hexlify(bytes_data).decode('utf-8')

def decode_hex_str_to_bytes(hex_str: str):
    return binascii.unhexlify(hex_str)

def get_encoder(encoding_type: str) -> callable:
    if not isinstance(encoding_type, str):
        raise ERR_T_ENC_1
    if encoding_type == "base64":
        return encode_bytes_to_base64_str
    elif encoding_type == "base58":
        return encode_bytes_to_base58_str
    elif encoding_type == "hex":
        return encode_bytes_to_hex_str
    else:
        raise ERR_N_ENC_1
    
def get_decoder(encoding_type: str) -> callable:
    if not isinstance(encoding_type, str):
        raise ERR_T_ENC_1
    if encoding_type == "base64":
        return decode_base64_str_to_bytes
    elif encoding_type == "base58":
        return decode_base58_str_to_bytes
    elif encoding_type == "hex":
        return decode_hex_str_to_bytes
    else:
        raise ERR_N_ENC_1
    
def encode_bytes(data: bytes, encoding_type: str):
    encoder = get_encoder(encoding_type)
    return encoder(data)

def decode_bytes(data: str, encoding_type: str):
    decoder = get_decoder(encoding_type)
    return decoder(data)
    
key_encoder = get_encoder(HASH_ENCODING_STYLE)
key_decoder = get_decoder(HASH_ENCODING_STYLE)