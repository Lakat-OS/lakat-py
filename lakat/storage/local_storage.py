from utils.trie.merkle_trie import MerkleTrie
from db.namespaces import NAME_RESOLUTION_TRIE_NS, DATA_TRIE_NS, INTERACTION_TRIE_NS
from config.encode_cfg import DEFAULT_CODEC
from typing import List, Tuple
from setup import storage
from lakat.errors import ERR_N_TRIE_1

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
