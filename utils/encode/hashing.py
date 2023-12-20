import multihash
import base58
import hashlib
import cid
from config.env import DEV_ENVIRONMENT
from config.encode_cfg import (
    ALGORITHM, DEV_HASH_LENGTH, ENCODING_FUNCTION, MH_BRANCHID_PREFIX_LENGTH, CODEC)

def get_hashing_algorithm(algorithm):
    if algorithm.startswith('sha2-'):
        hash_length = int(algorithm.split('-')[1])
        return 'sha' + str(hash_length)
    else:
        return algorithm
    

def __get_multihash_from_bytes(bytes_data):
    hashlib_algorithm = get_hashing_algorithm(ALGORITHM)
    sha256_hash = hashlib.__getattribute__(hashlib_algorithm)(bytes_data).digest()
    return multihash.encode(sha256_hash, ALGORITHM)


def get_multihash(data: str):
    bytes_data = data.encode(ENCODING_FUNCTION)
    return __get_multihash_from_bytes(bytes_data)


def encode_bytes_to_str(data: bytes):
    return base58.b58encode(data).decode(ENCODING_FUNCTION)


def decode_encoding_to_bytes(encoding: str):
    return base58.b58decode(encoding.encode(ENCODING_FUNCTION))


def lakatmultihash(data: str) -> str:
    mh = get_multihash(data=data)
    if DEV_ENVIRONMENT not in ["PROD", "QA"]:
        mh = mh[:DEV_HASH_LENGTH]
    return encode_bytes_to_str(mh)


def lakatcid(data: str):
    hsh = lakatmultihash(data=data)
    return cid.make_cid(1, CODEC, hsh).encode().decode(ENCODING_FUNCTION)





    
