"""
This module provides utility functions for working with Merkle tries in the Lakat system.
It offers a simplified interface for trie operations such as insertion, retrieval, and persistence.
"""

# from setup.db_trie import db
from setup.db_trie import cached_tries, db
from utils.trie.merkle_trie import MerkleTrie


def trie_insert(branchId, key, value):
    """
    Insert a key-value pair into the trie associated with the given branch ID.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        key: The key to insert
        value: The value to associate with the key
    """
    trie = get_trie(branchId)
    trie.insert(key, value)

def trie_insert_many(branchId, keysValuePairs):
    """
    Insert multiple key-value pairs into the trie associated with the given branch ID.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        keysValuePairs: Iterable of (key, value) tuples to insert
    """
    for key, value in keysValuePairs:
        trie_insert(branchId, key, value)

def trie_update_many_interactions(branchId, keysInteractionPairs):
    """
    Update multiple interactions in the trie associated with the given branch ID.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        keysInteractionPairs: Iterable of (key, interaction) tuples to update
    """
    for key, interaction in keysInteractionPairs:
        trie_update_interaction(branchId, key, interaction)

def trie_update_interaction(branchId, key, interaction):
    """
    Update an interaction for a specific key in the trie.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        key: The key whose interaction to update
        interaction: The interaction data to update
    """
    trie = get_trie(branchId)
    trie.update_interaction(key, interaction)

def trie_retrieve_value(branchId, key):
    """
    Retrieve a value for a given key from the trie.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        key: The key to retrieve the value for
        
    Returns:
        The value associated with the key, or None if not found
    """
    trie = get_trie(branchId)
    return trie.retrieve_value(key)

def trie_retrieve_interaction(branchId, key):
    """
    Retrieve an interaction for a given key from the trie.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        key: The key to retrieve the interaction for
        
    Returns:
        The interaction associated with the key, or None if not found
    """
    trie = get_trie(branchId)
    return trie.retrieve_interaction(key)

def trie_persist(branchId, interaction):
    """
    Persist the trie to the database with the given interaction.
    
    Parameters:
        branchId: The identifier for the branch whose trie to persist
        interaction: The interaction data to include in the persistence
    """
    trie = get_trie(branchId)
    trie.persist(interaction=interaction)

def trie_get_root_hash(branchId):
    """
    Get the root hash of the trie associated with the given branch ID.
    
    Parameters:
        branchId: The identifier for the branch whose trie to use
        
    Returns:
        The root hash of the trie
    """
    trie = get_trie(branchId)
    return trie.get_root_hash()

def get_trie(trie_root, branchId):
    """
    Get the trie for a given branch ID, creating it if necessary.
    
    This function checks if the trie is already cached, and if not,
    creates a new trie and loads it from the database.
    
    Parameters:
        trie_root: The root hash of the trie to load
        branchId: The identifier for the branch whose trie to get
        
    Returns:
        The MerkleTrie instance for the given branch ID
        
    Note:
        There are known issues with trie versioning that need to be addressed.
    """
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