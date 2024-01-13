import lakat.storage.local_storage as lakat_storage
from utils.encode.hashing import deserialize_from_key

def _get_branch_data_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    branch_state_id = lakat_storage.get_from_db(branch_id)
    serialized_branch_data = lakat_storage.get_from_db(branch_state_id)
    return deserialize_from_key(key=branch_state_id, value=serialized_branch_data)

def get_name_resolution_id_from_branch_id(branch_id: bytes) -> bytes:
    return _get_branch_data_from_branch_id(branch_id)["name_resolution"]

def get_data_trie_id_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    submit_id = _get_branch_data_from_branch_id(branch_id)["stable_head"]
    submit_data = deserialize_from_key(key=submit_id, value=lakat_storage.get_from_db(submit_id))
    return submit_data["trie_root"]

def get_interaction_id_from_branch_id(branch_id: bytes) -> bytes:
    return _get_branch_data_from_branch_id(branch_id)["interaction"]