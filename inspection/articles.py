import lakat.storage.trie_storage as lakat_trie_storage
import lakat.storage.local_storage as lakat_storage
import random
from inspection.branch import (
    _get_branch_data_from_branch_state_id,
    _get_registered_names_from_submit_trace_id)
from inspection.submits import (
    _find_branches_between_two_submits,
    _get_submit_trace_from_submit_id,
    _get_branch_id_from_submit_id)
from utils.encode.hashing import deserialize_from_key
from utils.encode.language import encode_string_standard, join_encoded_bytes
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA
from config.query_cfg import NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY, MAX_NUMBER_OF_SUBMIT_QUERIES
from typing import List, Tuple


def _get_article_id_from_article_name(branch_id: bytes, name: bytes) -> bytes:
    ## get the branch using get_branch_head_data_from_branch_id
    branch_head_data = _get_branch_data_from_branch_state_id(branch_state_id=lakat_storage.get_from_db(branch_id))
    ## get the name resolution data from trie
    temp_get_request_token = random.randint(1, 2**32-1)
    name = lakat_trie_storage.get_name_trie(branch_id=branch_id, branch_suffix=branch_head_data["ns"], key=name, 
    token=temp_get_request_token)
    lakat_trie_storage.clear_staged_name_trie_changes(branch_id=branch_id, token=temp_get_request_token)
    return name


def _get_data_from_bucket(bucket_id: bytes) -> bytes:
    bucket = deserialize_from_key(key=bucket_id, value=lakat_storage.get_from_db(bucket_id))
    if bucket["schema_id"]==DEFAULT_MOLECULAR_BUCKET_SCHEMA:

        overall_encoded_data = encode_string_standard("")
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

get_article_from_article_name_schema = {
  "type": "object",
  "properties": {
    "branch_id": {"type": "string", "format": "byte"},
    "name": {"type": "string", "varint_encoded": "true"}
  },
  "required": ["branch_id", "name"],
  "response": {"type": "string", "varint_encoded": "true"}
}


def get_article_ids_until_submit_id(branch_id: bytes, until_submit_id: bytes):
    branch_head_data = _get_branch_data_from_branch_state_id(branch_state_id=lakat_storage.get_from_db(branch_id))
    return _get_article_ids_between_two_submits(
        from_submit_id=branch_head_data["stable_head"], 
        until_submit_id=until_submit_id,
        allow_branch_hopping=True)
    
def get_article_ids_from_branch_id(branch_id: bytes):
    return get_article_ids_from_last_n_submits(
        branch_id=branch_id,
        number_of_submits=MAX_NUMBER_OF_SUBMIT_QUERIES,
        allow_branch_hopping=False)

def get_article_ids_from_last_n_submits(branch_id: bytes, number_of_submits: int, allow_branch_hopping: bool) -> List[any]:
    branch_head_data = _get_branch_data_from_branch_state_id(branch_state_id=lakat_storage.get_from_db(branch_id))
    number_of_submits = min(MAX_NUMBER_OF_SUBMIT_QUERIES, number_of_submits)
    registered_articles, retrieved_all_flag = _get_n_article_ids_from_submit_id(
        from_submit_id=branch_head_data["stable_head"], 
        until_submit_id=bytes(0),   ## No need to check until submit
        number_of_iterations=number_of_submits, 
        allow_branch_hopping=allow_branch_hopping)
    return registered_articles, retrieved_all_flag
    

def _get_n_article_ids_from_submit_id(from_submit_id: bytes, until_submit_id: bytes, number_of_iterations:int, allow_branch_hopping: bool) -> List[bytes]:
    check_until_submit_id_condition = until_submit_id != b""
    retrieved_all_articles_between_two_submits = (False if check_until_submit_id_condition else True)
    registered_articles = list()
    submit_id = from_submit_id
    branch_id = _get_branch_id_from_submit_id(submit_id=from_submit_id)
    for i in range(number_of_iterations):
        submit_trace = _get_submit_trace_from_submit_id(submit_id=submit_id)
        if submit_trace["branchId"] != branch_id and not allow_branch_hopping:
            retrieved_all_articles_between_two_submits = False
            break
        registered_articles.extend([dict(name=name[0], article_id=name[1], submit_id=submit_id, branch_id=submit_trace["branchId"]) for name in submit_trace["nameResolution"]])
        if submit_id==until_submit_id and check_until_submit_id_condition:
            retrieved_all_articles_between_two_submits = True
            break
    return registered_articles, retrieved_all_articles_between_two_submits

def _get_article_ids_between_two_submits(from_submit_id: bytes, until_submit_id: bytes, allow_branch_hopping: bool) -> List[bytes]:
    ## get the branch using get_branch_head_data_from_branch_id
    # _find_branch_id_between_two_submits
    found, _, branches = _find_branches_between_two_submits(
        from_submit_id=from_submit_id, until_submit_id=until_submit_id, number_of_branches_to_query=NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY)
    if not found:
        raise Exception(f"No connection has been found between the two submits or the maximum depth (={NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY}) of allowed ancentoral branches has been reached. Try to divide your query into smaller chunks.")
    if not allow_branch_hopping and branches[-1]!=branches[0]:
        raise Exception(f"The two specified submit ids are on different branches and you specified allow_branch_hopping=False.")
    
    return _get_n_article_ids_from_submit_id(
        from_submit_id=from_submit_id, 
        until_submit_id=until_submit_id, 
        number_of_iterations=MAX_NUMBER_OF_SUBMIT_QUERIES,
        allow_branch_hopping=allow_branch_hopping)

