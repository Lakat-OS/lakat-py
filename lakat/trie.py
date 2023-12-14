
# from setup.db_trie import db
from setup.db_trie import trie

# def create_trie(branchId):

def trie_insert(branchId, key, value):
    trie.insert(key, value)

def trie_insert_many(branchId, keysValuePairs):
    for key, value in keysValuePairs:
        trie_insert(branchId, key, value)

def trie_update_many_interactions(branchId, keysInteractionPairs):
    for key, interaction in keysInteractionPairs:
        trie_update_interaction(branchId, key, interaction)

def trie_update_interaction(branchId, key, interaction):
    trie.update_interaction(key, interaction)

def trie_retrieve_value(branchId, key):
    return trie.retrieve_value(key)

def trie_retrieve_interaction(branchId, key):
    return trie.retrieve_interaction(key)

def trie_persist(branchId, interaction):
    trie.persist(interaction=interaction)

def trie_get_root_hash(branchId):
    return trie.get_root_hash()