from setup import storage
from utils.trie.merkle_trie import MerkleTrie
from db.namespaces import NAME_RESOLUTION_TRIE_NS, DATA_TRIE_NS, INTERACTION_TRIE_NS

# clear db and start a new db
def restart_db():
    return storage.db_interface.restart()


def restart_db_with_name(name: str):
    return storage.db_interface.restart(name=name)


def create_name_trie(branch_id: bytes, branch_suffix: bytes):
    storage.name_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=NAME_RESOLUTION_TRIE_NS)


def create_data_trie(branch_id: bytes, branch_suffix: bytes):
    storage.data_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=DATA_TRIE_NS)


def create_interaction_trie(branch_id: bytes, branch_suffix: bytes):
    storage.interaction_tries[branch_id] = MerkleTrie(db=storage.db_interface, branch_suffix=branch_suffix, namespace=INTERACTION_TRIE_NS)


def put_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if not branch_id in storage.name_tries:
        create_name_trie(branch_id, branch_suffix)
    storage.name_tries[branch_id].put(key, value)


def put_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if not branch_id in storage.data_tries:
        create_data_trie(branch_id, branch_suffix)
    storage.data_tries[branch_id].put(key, value)


def put_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes):
    if not branch_id in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix)
    storage.interaction_tries[branch_id].put(key, value)


def stage_name_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if not branch_id in storage.name_tries:
        create_name_trie(branch_id, branch_suffix)
    return storage.name_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)


def stage_data_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if not branch_id in storage.data_tries:
        create_data_trie(branch_id, branch_suffix)
    return storage.data_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)


def stage_interaction_trie(branch_id: bytes, branch_suffix: bytes, key: bytes, value: bytes, codec: int = 0x0, inplace=True):
    if not branch_id in storage.interaction_tries:
        create_interaction_trie(branch_id, branch_suffix)
    return storage.interaction_tries[branch_id].stage(key=key, value=value, codec=codec, inplace=inplace)

