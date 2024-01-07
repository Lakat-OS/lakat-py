from typing import List, Mapping
from config.encode_cfg import DEFAULT_CODEC
from config.bucket_cfg import BUCKET_ID_TYPE_NO_REF, BUCKET_ID_TYPE_WITH_ID_REF
from interfaces.bucket import BUCKET
from lakat.timestamp import getTimestamp
from lakat.errors import ERR_T_BCKT_1
from utils.encode.hashing import make_lakat_cid_and_serialize


def prepare_bucket(content_dict: Mapping[str, any], namespace: int) -> bytes:
    bucket = BUCKET(
        schema_id = content_dict["schema_id"],
        signature = content_dict["signature"],
        public_key = content_dict["public_key"],
        parent_bucket = content_dict["parent_bucket"],
        data = content_dict["data"],
        refs = content_dict["refs"],
        timestamp = getTimestamp()
    )
    return make_lakat_cid_and_serialize(content=bucket.__dict__, codec=DEFAULT_CODEC, namespace=namespace, branch_id_1= bytes(0), branch_id_2=bytes(0), crop=0)
    

def get_bucket_ids_from_order(order: List[Mapping[str,any]], index_to_bucket_id):
    content_bucket_ids = []
    for entry in order:
        if entry["type"] == BUCKET_ID_TYPE_NO_REF:
            content_bucket_ids.append(index_to_bucket_id[entry["id"]])
        elif entry["type"] == BUCKET_ID_TYPE_WITH_ID_REF:
            content_bucket_ids.append(entry["id"])
        else:
            raise ERR_T_BCKT_1
    return content_bucket_ids