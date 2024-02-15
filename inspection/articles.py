import lakat.storage.trie_storage as lakat_trie_storage
import lakat.storage.local_storage as lakat_storage
import random
from inspection.branch import (
    _get_branch_data_from_branch_state_id,
    _get_registered_names_from_submit_trace_id)
from inspection.submits import (
    _find_branches_between_two_submits,
    _get_submit_trace_from_submit_id,
    _get_branch_id_from_submit_id,
    _get_submit_from_submit_id,
    _get_submit_trace_from_submit_trace_id)
from inspection.bucket import (
    _get_bucket_head_from_bucket_id)
from utils.encode.hashing import deserialize_from_key
from utils.encode.language import encode_string_standard, join_encoded_bytes
from config.bucket_cfg import DEFAULT_ATOMIC_BUCKET_SCHEMA, DEFAULT_MOLECULAR_BUCKET_SCHEMA
from config.query_cfg import NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY, MAX_NUMBER_OF_SUBMIT_QUERIES
from config.response_cfg import (
    TRIE_SUCCESS_CODE, 
    TRIE_ERROR_CODE_NODE_DOES_NOT_HAVE_THIS_CHILD,
    ARTICLE_NOT_FOUND_RESPONSE_CODE, 
    ARTICLE_NOT_FOUND_TRIE_LOOKUP_ERROR,
    ARTICLE_FOUND_RESPONSE_CODE, 
    ARTICLE_NOT_FOUND_DB_RESPONSE_BAD)
from typing import List, Tuple, Mapping

# FIXME: This should be _get_article_root_id_from_article_id
def _get_article_root_id_from_article_name(branch_id: bytes, name: bytes, number_of_branches_to_query: int) -> Tuple[bytes, int, bytes, int]:
    resp_code_dep_on_trie = lambda x : (ARTICLE_NOT_FOUND_TRIE_LOOKUP_ERROR
                if x else ARTICLE_NOT_FOUND_RESPONSE_CODE)
    previous_branch_id = branch_id
    current_branch_id = branch_id
    possible_trie_error = False
    parent_name_resolution_id=bytes(0)
    for i in range(number_of_branches_to_query):
        branch_state_id = lakat_storage.get_from_db(current_branch_id)
        if not branch_state_id:
            return bytes(0), ARTICLE_NOT_FOUND_DB_RESPONSE_BAD, previous_branch_id, i
        branch_head_data = _get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
        # consider two cases. 
        # Either the name is in the starting branch or it is in one 
        # of the ancestral branches
        if i==0:
            # check if the name is in the starging branch (i.e. i=0)
            temp_get_request_token = random.randint(1, 2**32-1)
            article_root_id, trie_response_code = lakat_trie_storage.get_name_trie(
                branch_id=current_branch_id, branch_suffix=branch_head_data["ns"], 
                key=name, token=temp_get_request_token)
            lakat_trie_storage.clear_staged_name_trie_changes(branch_id=branch_id, token=temp_get_request_token)
        else: 
            # check if the name is in the parent branch 
            # For that we can check the parent_data_tries_at_root_submit, which maps
            # the child branch id to the parent branch name resolution root id 
            # at the branching submit.
            article_root_id, trie_response_code = lakat_trie_storage.get_parent_data_trie_value(previous_branch_id, parent_name_resolution_id, name)

        if trie_response_code==TRIE_SUCCESS_CODE:
            return article_root_id, ARTICLE_FOUND_RESPONSE_CODE, current_branch_id, i

        # there is some other trie error (not related to the entry not existing)
        possible_trie_error = trie_response_code!=TRIE_ERROR_CODE_NODE_DOES_NOT_HAVE_THIS_CHILD

        # the name is certainly not in this trie. Let's try the parent branch
        parent_name_resolution_id = branch_head_data["parent_name_resolution"]
        if parent_name_resolution_id==bytes(0):
            # search is over
            return bytes(0), resp_code_dep_on_trie(possible_trie_error), current_branch_id, i

        # update the current branch id for the next iteration.
        previous_branch_id = current_branch_id
        current_branch_id = branch_head_data["parent_id"]

    # search is over (nothing was found).
    return bytes(0), resp_code_dep_on_trie(possible_trie_error), previous_branch_id, i


def get_article_root_id_from_article_name(branch_id: bytes, name: bytes) -> Mapping[str, bytes or int]:
    article_root_id, response_code, at_branch, branch_iterations = _get_article_root_id_from_article_name(branch_id=branch_id, name=name, number_of_branches_to_query=NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY)
    return {"article_root_id": article_root_id, "response_code": response_code, "at_branch": at_branch, "branch_iterations": branch_iterations}

get_article_root_id_from_article_name_schema = {
    "type": "object",
    "properties": {
        "branch_id": {"type": "string", "format": "byte"},
        "name": {"type": "string", "varint_encoded": "true"}
    },
    "required": ["branch_id", "name"],
    "response": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "varint_encoded": "true"},
            "response_code": {"type": "integer"},
            "at_branch": {"type": "string", "format": "byte"},
            "branch_iterations": {"type": "integer"}
        },
        "required": ["name", "response_code", "at_branch", "branch_iterations"]
    }
}

def _get_data_from_bucket(bucket_id: bytes) -> bytes:
    bucket_serialized = lakat_storage.get_from_db(bucket_id)
    bucket = deserialize_from_key(key=bucket_id, value=bucket_serialized)
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
    article_root_id, response_code, at_branch, branch_iterations = _get_article_root_id_from_article_name(branch_id=branch_id, name=name, number_of_branches_to_query=NUMBER_OF_BRANCHES_TO_TRAVERSE_ON_QUERY)
    if response_code!=ARTICLE_FOUND_RESPONSE_CODE:
        return {
            "article": encode_string_standard(""), 
            "response_code": response_code, 
            "at_branch": at_branch}
    # FIXME: MUST NOT GET THE HEAD OF THE BUCKET, IF ITS FROM A PARENT BRANCH
    bucket_head_id, trie_response_code = _get_bucket_head_from_bucket_id(branch_id=at_branch, bucket_id=article_root_id) 
    if trie_response_code!=TRIE_SUCCESS_CODE:
        return {
            "article": encode_string_standard(""), 
            "response_code": ARTICLE_NOT_FOUND_TRIE_LOOKUP_ERROR, 
            "at_branch": at_branch}
    return {
        "article": _get_data_from_bucket(bucket_id=bucket_head_id),
        "response_code": response_code,
        "at_branch": at_branch}

get_article_from_article_name_schema = {
  "type": "object",
  "properties": {
    "branch_id": {"type": "string", "format": "byte"},
    "name": {"type": "string", "varint_encoded": "true"}
  },
  "required": ["branch_id", "name"],
  "response": {
    "type": "object",
    "properties": {
        "article": {"type": "string", "varint_encoded": "true"},
        "response_code": {"type": "integer"},
        "at_branch": {"type": "string", "format": "byte"}
    },
    "required": ["article", "response_code", "at_branch"]
  }
}

def get_article_from_article_id(bucket_id: bytes) -> bytes:
    return _get_data_from_bucket(bucket_id=bucket_id)

get_article_from_article_id_schema = {
    "type": "object",
    "properties": {
        "bucket_id": {"type": "string", "format": "byte"}
    },
    "required": ["bucket_id"],
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
        submit = _get_submit_from_submit_id(submit_id=submit_id)
        submit_trace = _get_submit_trace_from_submit_trace_id(submit_trace_id=submit["submit_trace"])
        if submit_trace["branchId"] != branch_id and not allow_branch_hopping:
            retrieved_all_articles_between_two_submits = False
            break
        registered_articles.extend([dict(name=name[0], article_id=name[1], submit_id=submit_id, branch_id=submit_trace["branchId"]) for name in submit_trace["nameResolution"]])

        if submit_id==until_submit_id and check_until_submit_id_condition:
            retrieved_all_articles_between_two_submits = True
            break
        if submit["parent_submit_id"]==b"":
            retrieved_all_articles_between_two_submits = True
            break
        submit_id = submit["parent_submit_id"]

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

