from ipld import multihash

def hash(data: bytes) -> str:
    return multihash(data = data, fn_name = 'sha2_256')