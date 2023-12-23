
# from setup.db_trie import db
from setup.db_trie import cached_tries, db
from utils.trie.trie import MerkleTrie


def trie_insert(branchId, key, value):
    trie = get_trie(branchId)
    trie.insert(key, value)

def trie_insert_many(branchId, keysValuePairs):
    for key, value in keysValuePairs:
        trie_insert(branchId, key, value)

def trie_update_many_interactions(branchId, keysInteractionPairs):
    for key, interaction in keysInteractionPairs:
        trie_update_interaction(branchId, key, interaction)

def trie_update_interaction(branchId, key, interaction):
    trie = get_trie(branchId)
    trie.update_interaction(key, interaction)

def trie_retrieve_value(branchId, key):
    trie = get_trie(branchId)
    return trie.retrieve_value(key)

def trie_retrieve_interaction(branchId, key):
    trie = get_trie(branchId)
    return trie.retrieve_interaction(key)

def trie_persist(branchId, interaction):
    trie = get_trie(branchId)
    trie.persist(interaction=interaction)

def trie_get_root_hash(branchId):
    trie = get_trie(branchId)
    return trie.get_root_hash()

def get_trie(trie_root, branchId):
    if branchId in cached_tries:
        return cached_tries[branchId]
    else:
        # create
        trie = MerkleTrie(db=db, branchId=branchId)
        # TODO: THERE SHOULD ALSO BE SOME SORT OF LAZY LOADING
        # TODO: THERE IS AN ISSUE WHEN THE TRIE IS NOT THE LAST VERSION OF THE TRIE. 
        # SO if at some later point i again want to getthe trie from the branchid and
        # suppose that i have already loaded the trie from the db, then i will get the
        # old version of the trie.
        trie.load_trie_from_db(trie_root)
        cached_tries[branchId] = trie
        return trie