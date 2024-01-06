import base58
import json
import hashlib
import multihash
from typing import Tuple
import multicodec
import cbor2
import varint
from config.env import DEV_ENVIRONMENT
from config.encode_cfg import (
    ALGORITHM, ENCODING_FUNCTION)
from config.dev_cfg import DEV_CID_CROP


def encode_bytes_to_str(data: bytes):
    return base58.b58encode(data).decode(ENCODING_FUNCTION)

def decode_encoding_to_bytes(encoding: str):
    return base58.b58decode(encoding.encode(ENCODING_FUNCTION))


def get_hashlib_algorithm(algorithm):
    if algorithm.startswith('sha2-'):
        hash_length = int(algorithm.split('-')[1])
        return 'sha' + str(hash_length)
    else:
        return algorithm
    
def get_multihash(data: bytes):
    if DEV_ENVIRONMENT in ["DEV", "LOCAL"]:
        return get_multihash_from_bytes(data, crop=DEV_CID_CROP)
    return get_multihash_from_bytes(data, crop=0)

def get_multihash_from_bytes(bytes_data: bytes, crop: int=0):
    return get_multihash_from_bytes_and_algorithm(bytes_data, ALGORITHM, crop=crop)

def get_multihash_from_bytes_and_algorithm(bytes_data: bytes, algorithm: str, crop: int=0):
    hashlib_algorithm = get_hashlib_algorithm(algorithm)
    sha256_hash = hashlib.__getattribute__(hashlib_algorithm)(bytes_data).digest()
    return get_multihash_from_digest_and_algorithm(sha256_hash, algorithm, crop=crop)

def get_multihash_from_digest_and_algorithm(digest: bytes, algorithm: str, crop: int=0):
    alg = varint.encode(multicodec.constants.NAME_TABLE[algorithm])
    digest_length = len(digest)
    crop = min(crop, digest_length - 1)
    digest_cropped = digest[:digest_length-crop]
    length = varint.encode(len(digest_cropped))
    return alg + length + digest_cropped

def get_multihash_from_str(str_data: str, crop: int=0):
    bytes_data = str_data.encode(ENCODING_FUNCTION)
    return get_multihash_from_bytes(bytes_data, crop=crop)

def varint_decode(data: bytes) -> Tuple[int, int]:
    """Decode a varint from bytes and return the value and length of the varint."""
    value, shift, length = 0, 0, 0
    for b in data:
        value |= (b & 0x7f) << shift
        shift += 7
        length += 1
        if not (b & 0x80):
            break
    return value, length

def make_cid(version: int, codec: int, multi_hash: bytes) -> bytes:
    """Create a CID from version, codec, and multihash."""
    version_bytes = varint.encode(version)
    codec_bytes = varint.encode(codec)
    return version_bytes + codec_bytes + multi_hash


def parse_cid(cid: bytes) -> Tuple[int, int, bytes]:
    """Parse a CID into version, codec, and multihash."""
    # Decode the version varint
    version, version_length = varint_decode(cid)
    # Decode the codec varint
    codec, codec_length = varint_decode(cid[version_length:])
    # The rest is the multihash
    multi_hash = cid[version_length + codec_length:]
    return version, codec, multi_hash

def encode_ns_and_suffix(namespace: int, suffix: bytes):
    return varint.encode(namespace) + varint.encode(len(suffix)) + suffix

def make_lakat_cid(codec:int, multi_hash: bytes, namespace: int, suffix: bytes):
    cid_1 = make_cid(version=1, codec=codec, multi_hash=multi_hash)
    return cid_1 + encode_ns_and_suffix(namespace=namespace, suffix=suffix)

def parse_lakat_cid(lakat_cid: bytes):
    # parse the lakat_cid into version, codec and multihash_plus_suffix
    version, codec, multihash_plus_suffix = parse_cid(cid=lakat_cid)
    # Decode the algorithm varint
    alg_id, alg_id_length = varint_decode(multihash_plus_suffix)
    # Decode the codec varint
    digest_length, digest_length_length = varint_decode(multihash_plus_suffix[alg_id_length:])
    # Decode the multihash
    digest_plus_suffix = multihash_plus_suffix[(alg_id_length + digest_length_length):]
    # check for namespace and suffix
    if len(digest_plus_suffix)==digest_length:
        namespace = 0
        digest = digest_plus_suffix
        suffix_length_length = 0
        branch_id = bytes()
        parent_branch_id = bytes()
        crop = 0
    else:
        # decode the namespace and suffix
        namespace, namespace_length = varint_decode(digest_plus_suffix[digest_length:])
        # Decode the suffix length varint
        suffix_length, suffix_length_length = varint_decode(digest_plus_suffix[digest_length + namespace_length:])
        # split the suffix in two
        suffix = digest_plus_suffix[digest_length + namespace_length + suffix_length_length:]
        digest = digest_plus_suffix[:digest_length]
        crop = suffix_length
        branch_id = suffix[0:int(crop/2)]
        parent_branch_id = suffix[int(crop/2):]

    return version, codec, alg_id, digest_length, digest, namespace, suffix_length_length, crop, branch_id, parent_branch_id        

def make_suffix_from_branch_ids(branch_id_1: bytes, branch_id_2: bytes, crop: int):
    digest_1 = scramble_id(cid=branch_id_1)
    if branch_id_2 == bytes(0):
        return digest_1[:crop] + bytes(crop)
    digest_2 = scramble_id(cid=branch_id_2)
    return digest_1[:crop] + digest_2[:crop]

def scramble_id(cid: bytes):
    hashlib_algorithm = get_hashlib_algorithm_from_cid(cid)
    return hashlib.__getattribute__(hashlib_algorithm)(cid).digest()

def get_hashlib_algorithm_from_cid(cid: bytes) -> int:
    _, _, mh = parse_cid(cid)
    alg_id, _ = varint_decode(mh) 
    algorithm = multihash.constants.CODE_HASHES[alg_id]
    return get_hashlib_algorithm(algorithm)

def make_lakat_cid_and_serialize(content: any, codec: int, namespace: int, branch_id_1: bytes, branch_id_2: bytes, crop: int):
    s = serialize(content=content, codec=codec)
    mh = get_multihash(s)
    if namespace==0:
        return make_cid(version=1, codec=codec, multi_hash=mh), s
    if branch_id_1 == bytes(0):
        raise Exception("Branch_ids need to be supplied!")
    suffix = make_suffix_from_branch_ids(branch_id_1=branch_id_1, branch_id_2=branch_id_2, crop=crop)
    cid_1 = make_lakat_cid(codec=codec, multi_hash=mh, namespace=namespace, suffix=suffix)
    return cid_1, s

def make_lakat_cid_and_serialize_from_suffix(content: any, codec: int, namespace: int, suffix: bytes):
    s = serialize(content=content, codec=codec)
    mh = get_multihash(s)
    if namespace==0:
        return make_cid(version=1, codec=codec, multi_hash=mh), s
    cid_1 = make_lakat_cid(codec=codec, multi_hash=mh, namespace=namespace, suffix=suffix)
    return cid_1, s

def serialize(content: any, codec: int):
    codec_name = multicodec.constants.CODE_TABLE[codec]
    if codec_name=='cbor':
        return cbor2.dumps(content)
    else:
        raise Exception('No codec found')
    
def deserialize(data: bytes, codec: int) -> any:
    codec_name = multicodec.constants.CODE_TABLE[codec]
    if codec_name=='cbor':
        return cbor2.loads(data)
    else:
        raise Exception('No codec found')

def deserialize_from_key(key: bytes, value: bytes) -> any:
    version, codec_id, mh = parse_cid(key)
    return deserialize(data=value, codec=codec_id)
    
def get_namespace_from_lakat_cid(lakat_cid: bytes):
    # parse the lakat_cid into version, codec and multihash_plus_suffix
    _, _, multihash_plus_suffix = parse_cid(cid=lakat_cid)
    # Decode the algorithm varint
    _, alg_id_length = varint_decode(multihash_plus_suffix)
    # Decode the codec varint
    digest_length, digest_length_length = varint_decode(multihash_plus_suffix[alg_id_length:])
    # Decode the multihash
    digest_plus_suffix = multihash_plus_suffix[(alg_id_length + digest_length_length):]
    # check for namespace and suffix
    if len(digest_plus_suffix)==digest_length:
        return 0
    namespace, _ = varint_decode(digest_plus_suffix[digest_length:])
    return namespace


def hexlify(data):
    return [(byte >> 4 if high_nibble else byte & 0x0F) for byte in data for high_nibble in [True, False]]
    



    
