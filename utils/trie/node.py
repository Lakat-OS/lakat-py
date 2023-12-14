from utils.serialize import serialize
from utils.encode.hashing import lakathash
from config.db_cfg import TRIE_TYPE

class TrieNode:
    def __init__(self, path=''):
        self.children = {}
        self.value : str or None = None
        self.hash = None
        self.interaction = None
        self.path = path
    
    @property
    def is_leaf(self):
        """
        Property to determine if the node is a leaf.
        A node is considered a leaf if it has no children
        """
        return len(self.children) == 0

    @property
    def is_junction(self):
        """
        Property to determine if the node is a junction.
        A node is considered a junction if it has more than one child or it holds a value.
        """
        return len(self.children) > 1 or self.value is not None
    

    def update_hash(self, db):
        # Combine the hash of the value with the hashes of the children
        # serialize the data of the node except the hash
        serialized_data = self.serialize()
        self.hash = lakathash(serialized_data)
        db.put(self.hash.encode('utf-8'), serialized_data, entry_type=TRIE_TYPE)
        

    def serialize(self):
        data = dict()
        for k,v in self.__dict__.items():
            if k == 'hash':
                continue
            if k == 'children':
                data[k] = {l: node.hash for l, node in v.items()}
            else:
                data[k] = v
        return serialize(data)

    def get_hash(self):
        serialized_data = self.serialize()
        return lakathash(serialized_data)

    def __repr__(self):
        return f"TrieNode({self.hash[:10]})"
