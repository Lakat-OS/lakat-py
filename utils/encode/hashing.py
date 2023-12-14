from ipld import multihash
from config.env import DEV_ENVIRONMENT, DEV_HASH_LENGTH

def lakathash(data: bytes) -> str:
    mh = multihash(data = data, fn_name = 'sha2_256')
    if DEV_ENVIRONMENT not in ["PROD", "QA"]:
        return mh[:DEV_HASH_LENGTH]
    return mh