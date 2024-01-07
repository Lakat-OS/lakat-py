from utils.trie.merkle_trie import MerkleTrie
from db.namespaces import NAME_RESOLUTION_TRIE_NS, DATA_TRIE_NS, INTERACTION_TRIE_NS
from config.encode_cfg import DEFAULT_CODEC
from typing import List, Tuple
from setup import storage

# clear db and start a new db
def restart_db():
    return storage.db_interface.restart()

def restart_db_with_name(name: str):
    return storage.db_interface.restart(name=name)

def stage_to_db(key: bytes, value: bytes):
    storage.db_interface.stage(key=key, value=value)

def stage_many_to_db(entries: List[Tuple[bytes, bytes]]) -> None:
    storage.db_interface.stage_many(entries)

def commit_to_db():
    storage.db_interface.commit()    

def get_from_db(key: bytes) -> bytes:
    return storage.db_interface.get(key)

def create_name_trie(branch_id: bytes, branch_suffix: bytes):
    storage.name_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=NAME_RESOLUTION_TRIE_NS)


def create_data_trie(branch_id: bytes, branch_suffix: bytes):
    storage.data_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=DATA_TRIE_NS)


def create_interaction_trie(branch_id: bytes, branch_suffix: bytes):
    storage.interaction_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=INTERACTION_TRIE_NS)


def ensure_name_trie(func):
    def wrapper(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
        if branch_id not in storage.data_tries:
            create_name_trie(branch_id, branch_suffix)
        return func(branch_id, key, value)
    return wrapper


def ensure_data_trie(func):
    def wrapper(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
        if branch_id not in storage.data_tries:
            create_data_trie(branch_id, branch_suffix)
        return func(branch_id, key, value)
    return wrapper


def ensure_interaction_trie(func):
    def wrapper(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
        if branch_id not in storage.data_tries:
            create_interaction_trie(branch_id, branch_suffix)
        return func(branch_id, key, value)
    return wrapper


# @ensure_name_trie
# def put_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
#     storage.name_tries[branch_id].put(key, value)

# @ensure_data_trie
# def put_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
#     storage.data_tries[branch_id].put(key, value)

# @ensure_interaction_trie
# def put_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
#     storage.interaction_tries[branch_id].put(key, value)

# @ensure_name_trie
def stage_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True)->Tuple[bytes, dict]:
    if branch_id not in storage.name_tries:
        create_name_trie(branch_id, branch_suffix)
    codec==(DEFAULT_CODEC if codec==0x0 else codec)
    print("codec in stage_name_trie is", codec)
    return storage.name_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

# @ensure_data_trie
def stage_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if branch_id not in storage.data_tries:
        create_data_trie(branch_id, branch_suffix)
    return storage.data_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

# @ensure_interaction_trie
def stage_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if branch_id not in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix)
    return storage.interaction_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

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