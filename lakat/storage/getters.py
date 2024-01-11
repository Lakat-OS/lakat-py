import lakat.storage.local_storage as lakat_storage
from utils.encode.hashing import deserialize_from_key


def get_branch_head_id_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    return lakat_storage.get_from_db(branch_id)


## branch data ##

def get_branch_data_from_branch_state_id(branch_state_id: bytes) -> dict:
    ## get the branch head
    serialized_branch_data =  lakat_storage.get_from_db(branch_state_id)
    return deserialize_from_key(key=branch_state_id, value=serialized_branch_data)

def get_branch_head_data_from_branch_id(branch_id: bytes) -> dict:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_branch_data_from_branch_state_id(branch_state_id=branch_head_id)

def get_branch_name_from_branch_state_id(branch_state_id: bytes) -> str:
    ## get the branch head
    branch_data = get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    return branch_data["name"]

def get_branch_name_from_branch_id(branch_id: bytes) -> str:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_branch_name_from_branch_state_id(branch_state_id=branch_head_id)

def get_branch_config_from_branch_state_id(branch_state_id: bytes) -> dict:
    ## get the branch head
    branch_data = get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    branch_config_id = branch_data["config"]
    return deserialize_from_key(key=branch_config_id, value=lakat_storage.get_from_db(branch_config_id))

def get_branch_config_from_branch_id(branch_id: bytes) -> dict:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_branch_config_from_branch_state_id(branch_state_id=branch_head_id)

def get_stable_head_from_branch_state_id(branch_state_id: bytes) -> bytes:
    ## get the branch head
    branch_data = get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    stable_head_id = branch_data["stable_head"]
    return deserialize_from_key(key=stable_head_id, value=lakat_storage.get_from_db(stable_head_id))

def get_stable_head_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_stable_head_from_branch_state_id(branch_state_id=branch_head_id)

def get_branch_type_from_branch_state_id(branch_state_id: bytes) -> str:
    ## get the branch config 
    branch_config = get_branch_config_from_branch_state_id(branch_state_id=branch_state_id)
    return branch_config["type"]

def get_branch_type_from_branch_id(branch_id: bytes) -> str:
    ## get the branch config 
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_branch_type_from_branch_state_id(branch_state_id=branch_head_id)

def get_name_resolution_id_from_branch_state_id(branch_state_id: bytes) -> bytes:
    ## get the branch head
    branch_data = get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    return branch_data["name_resolution"]

def get_name_resolution_id_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_name_resolution_id_from_branch_state_id(branch_state_id=branch_head_id)

def get_interaction_id_from_branch_state_id(branch_state_id: bytes) -> bytes:
    ## get the branch head
    branch_data = get_branch_data_from_branch_state_id(branch_state_id=branch_state_id)
    return branch_data["interaction"]

def get_interaction_id_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_interaction_id_from_branch_state_id(branch_state_id=branch_head_id)

def get_data_trie_id_from_branch_state_id(branch_state_id: bytes) -> bytes:
    ## get the branch head
    submit_data = get_stable_head_from_branch_state_id(branch_state_id=branch_state_id)
    return submit_data["trie_root"]

def get_data_trie_id_from_branch_id(branch_id: bytes) -> bytes:
    ## get the branch head
    branch_head_id = get_branch_head_id_from_branch_id(branch_id=branch_id)
    return get_data_trie_id_from_branch_state_id(branch_state_id=branch_head_id)

# def get_article_id_from_article_name(branch_id: bytes, name: str) -> bytes:
#     ## get the branch using get_branch_head_data_from_branch_id
#     branch_head_data = get_branch_head_data_from_branch_id(branch_id=branch_id)
#     ## get the name resolution
#     name_resolution_id = branch_head_data["name_resolution"]
#     ## get the name resolution data from trie
#     return lakat_storage.get_name_trie(branch_id=branch_id, branch_suffix=branch_head_data["ns"], key=name_resolution_id)



################# Articles #######################

# def get_article_id_from_article_name(branch_id: bytes, name: str):
#     ## get the branch head
#     pass