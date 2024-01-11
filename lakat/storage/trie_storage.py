from utils.trie.merkle_trie import MerkleTrie
from db.namespaces import NAME_RESOLUTION_TRIE_NS, DATA_TRIE_NS, INTERACTION_TRIE_NS
from config.encode_cfg import DEFAULT_CODEC
from typing import List, Tuple
from setup import storage
from lakat.errors import ERR_N_TRIE_1
from lakat.storage.getters import (
    get_name_resolution_id_from_branch_id,
    get_data_trie_id_from_branch_id,
    get_interaction_id_from_branch_id)

def create_name_trie(branch_id: bytes, branch_suffix: bytes, fetch_root: bool = False):
    storage.name_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=NAME_RESOLUTION_TRIE_NS)
    if fetch_root:
        root_id = get_name_resolution_id_from_branch_id(branch_id)
        storage.name_tries[branch_id].set_root(root_id=root_id)

def create_data_trie(branch_id: bytes, branch_suffix: bytes, fetch_root: bool = False):
    storage.data_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=DATA_TRIE_NS)
    if fetch_root:
        root_id = get_data_trie_id_from_branch_id(branch_id)
        storage.data_tries[branch_id].set_root(root_id=root_id)
    
def create_interaction_trie(branch_id: bytes, branch_suffix: bytes, fetch_root: bool = False):
    storage.interaction_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=INTERACTION_TRIE_NS)
    if fetch_root:
        root_id = get_interaction_id_from_branch_id(branch_id)
        storage.interaction_tries[branch_id].set_root(root_id=root_id)

def put_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if branch_id not in storage.name_tries:
        create_name_trie(branch_id, branch_suffix, fetch_root=True)
    storage.name_tries[branch_id].put(key, value)

def put_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if branch_id not in storage.data_tries:
        create_data_trie(branch_id, branch_suffix, fetch_root=True)
    storage.data_tries[branch_id].put(key, value)

def put_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if branch_id not in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix,  fetch_root=True)
    storage.interaction_tries[branch_id].put(key, value)

def stage_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True)->Tuple[bytes, dict]:
    if branch_id not in storage.name_tries:
        create_name_trie(branch_id, branch_suffix,  fetch_root=True)
    codec==(DEFAULT_CODEC if codec==0x0 else codec)
    return storage.name_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

# @ensure_data_trie
def stage_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if branch_id not in storage.data_tries:
        create_data_trie(branch_id, branch_suffix,  fetch_root=True)
    return storage.data_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

# @ensure_interaction_trie
def stage_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if branch_id not in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix,  fetch_root=True)
    return storage.interaction_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)


# @ensure_name_trie
def get_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes)->bytes:
    if branch_id not in storage.name_tries:
        create_name_trie(branch_id, branch_suffix,  fetch_root=True)
    res, code = storage.name_tries[branch_id].get(key=key)
    if code!=200:
        raise ERR_N_TRIE_1(code)
    return res
    

# @ensure_data_trie
def get_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes):
    if branch_id not in storage.data_tries:
        create_data_trie(branch_id, branch_suffix,  fetch_root=True)
    res, code = storage.data_tries[branch_id].get(key=key)
    if code!=200:
        raise ERR_N_TRIE_1(code)
    return res

# @ensure_interaction_trie
def get_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes):
    if branch_id not in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix,  fetch_root=True)
    res, code = storage.interaction_tries[branch_id].get(key=key)
    if code!=200:
        raise ERR_N_TRIE_1(code)
    return res


def stage_name_trie_root(branch_id: bytes, inplace: bool=False):
    # print('Default codec is', DEFAULT_CODEC)
    return storage.name_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=inplace)

def stage_data_trie_root(branch_id: bytes, inplace: bool=False):
    return storage.data_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=inplace)

def stage_interaction_trie_root(branch_id: bytes, inplace: bool=False):
    return storage.interaction_tries[branch_id].stage_root(codec=DEFAULT_CODEC, inplace=inplace)


# commit(self, staged_root=bytes(0), staged_db=[], staged_cache=dict(), inplace=True, commit_to_db=True):

def commit_name_trie_changes(branch_id: bytes, staged_root=bytes(0), staged_db=[], staged_cache=dict(), inplace: bool=False, commit_to_db: bool=False):
    # TODO: get rid of "moving the cahced stuff outside of the name trie"
    return storage.name_tries[branch_id].commit(staged_root=staged_root, staged_db=staged_db, staged_cache=staged_cache, inplace=inplace, commit_to_db=commit_to_db)

def commit_data_trie_changes(branch_id: bytes, staged_root=bytes(0), staged_db=[], staged_cache=dict(), inplace: bool=False, commit_to_db: bool=False):
    return storage.data_tries[branch_id].commit(staged_root=staged_root, staged_db=staged_db, staged_cache=staged_cache, inplace=inplace, commit_to_db=commit_to_db)

def commit_interaction_trie_changes(branch_id: bytes, staged_root=bytes(0), staged_db=[], staged_cache=dict(), inplace: bool=False, commit_to_db: bool=False):
    return storage.interaction_tries[branch_id].commit(staged_root=staged_root, staged_db=staged_db, staged_cache=staged_cache, inplace=inplace, commit_to_db=commit_to_db)