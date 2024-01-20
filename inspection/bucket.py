import lakat.storage.local_storage as lakat_storage
import lakat.storage.trie_storage as trie_storage
import inspection.branch as inspection_branch
from utils.encode.hashing import deserialize_from_key
from schema.bucket import bucket_schema
import random
from typing import Tuple, List


def _get_bucket_from_bucket_id(bucket_id: bytes) -> dict:
    return deserialize_from_key(bucket_id, lakat_storage.get_from_db(bucket_id))


def get_bucket_from_bucket_id(bucket_id: bytes) -> dict:
    return _get_bucket_from_bucket_id(bucket_id=bucket_id)

def _get_bucket_head_from_bucket_id(branch_id: bytes, bucket_id: bytes) -> dict:
    branch_dict = inspection_branch._get_branch_data_from_branch_state_id(
        branch_state_id=lakat_storage.get_from_db(branch_id))
    
    bucket = _get_bucket_from_bucket_id(bucket_id=bucket_id)
    bucket_root = bucket["root_bucket"]
    if not bucket_root:
        bucket_root = bucket_id

    temp_get_request_token = random.randint(1, 2**32-1)
    bucket_head_id = trie_storage.get_data_trie(
        branch_id=branch_id, 
        branch_suffix=branch_dict["ns"], 
        key=bucket_root, 
        token=temp_get_request_token)
    # clear staging area
    trie_storage.clear_staged_name_trie_changes(
        branch_id=branch_id, token=temp_get_request_token)

    return bucket_head_id
   
    
def get_bucket_head_from_bucket_id(branch_id: bytes, bucket_id: bytes, deserialize_bucket: bool) -> dict:
    bucket_head_id = _get_bucket_head_from_bucket_id(branch_id=branch_id, bucket_id=bucket_id)
    if not deserialize_bucket:
        return bucket_head_id
    else:
        return dict(
            id=bucket_head_id,
            data=_get_bucket_from_bucket_id(bucket_id=bucket_head_id))
        

get_bucket_from_bucket_id_schema = {
    "type": "object",
    "properties": {
        "bucket_id": {"type": "string", "format": "byte"},
    },
    "required": ["bucket_id"],
    "response": bucket_schema
}

get_bucket_head_from_bucket_id_schema = {
    "type": "object",
    "properties": {
        "branch_id": {"type": "string", "format": "byte"},
        "bucket_id": {"type": "string", "format": "byte"},
        "deserialize_bucket": {"type": "boolean"}
    },
    "required": ["branch_id", "bucket_id", "deserialize_bucket"],
    "response": {
        "oneOf": 
            [
                {"type": "string", "format": "byte"},
                {
                    "type": "object", 
                    "properties": {
                        "id": {"type": "string", "format": "byte"}, 
                        "data": bucket_schema}
                }
            ]
    }
}