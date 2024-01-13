import lakat.storage.trie_storage as lakat_trie_storage
import lakat.storage.local_storage as lakat_storage
import random
from inspection.branch import _get_branch_data_from_branch_state_id
from utils.encode.hashing import deserialize_from_key
from utils.encode.language import encode_string_standard, join_encoded_bytes
from helper.bucket_schema import is_molecular_bucket


def _get_article_id_from_article_name(branch_id: bytes, name: bytes) -> bytes:
    ## get the branch using get_branch_head_data_from_branch_id
    branch_head_data = _get_branch_data_from_branch_state_id(branch_id=lakat_storage.get_from_db(branch_id))
    ## get the name resolution data from trie
    temp_get_request_token = random.randint(1, 2**32-1)
    name = lakat_trie_storage.get_name_trie(branch_id=branch_id, branch_suffix=branch_head_data["ns"], key=name, token=temp_get_request_token)
    lakat_trie_storage.clear_staged_name_trie_changes(branch_id=branch_id, token=temp_get_request_token)
    return name

def _get_data_from_bucket(bucket_id: bytes) -> bytes:
    bucket = deserialize_from_key(key=bucket_id, value=lakat_storage.get_from_db(bucket_id))
    if is_molecular_bucket(bucket_id=bucket["schema_id"]):
        overall_encoded_data = encode_string_standard(b"")
        separator = encode_string_standard("\n")
        # TODO: also account for name
        for sub_bucket_id in bucket["data"]:
            overall_encoded_data = join_encoded_bytes([
                overall_encoded_data, 
                separator, 
                _get_data_from_bucket(sub_bucket_id)])
        return overall_encoded_data
    return bucket["data"]


def get_article_from_article_name(branch_id: bytes, name: bytes) -> bytes:
    article_id = _get_article_id_from_article_name(branch_id=branch_id, name=name)
    return _get_data_from_bucket(bucket_id=article_id)