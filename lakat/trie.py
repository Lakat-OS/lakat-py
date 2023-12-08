import hashlib
import binascii
from utils.encode.hashing import lakathash
from utils.serialize import serialize


def hexlify(data: str) -> str:
    return binascii.hexlify(data.encode('utf-8')).decode('utf-8')

# def hash_data(data):
#     return hashlib.sha256(data.encode('utf-8')).hexdigest()

class TrieNode:
    def __init__(self):
        self.children = {}
        self.value : str or None = None
        self.hash = None
        self.interaction = None
    
    @property
    def is_junction(self):
        """
        Property to determine if the node is a junction.
        A node is considered a junction if it has more than one child or it holds a value.
        """
        return len(self.children) > 1 or self.value is not None
    

    def update_hash(self):
        # Combine the hash of the value with the hashes of the children
        children_hash = ''.join(child.hash for child in self.children.values() if child.hash)
        combined = (children_hash + (self.value if self.value else '') + (self.interaction if self.interaction else '')).encode('utf-8')
        self.hash = lakathash(combined)

    def __repr__(self):
        return f"TrieNode({self.hash[:10]})"

class MerkleTrie:
    def __init__(self):
        self.root = TrieNode()
        self.update_history = []

    def reset_update_history(self):
        self.update_history = []

    def insert(self, key: str, value):
        self.reset_update_history()
        key_hex = hexlify(key)
        self._insert_node(self.root, key_hex, value, False)
        self.root.update_hash()
        self.update_history.reverse()

    def _insert_node(self, current_node: TrieNode, key, value, current_node_is_new=False):
        self.update_history.append({
            "node": current_node, 
            "hash": current_node.hash, 
            "value": current_node.value, 
            "interaction": current_node.interaction, 
            "children": current_node.children,
            "new": current_node_is_new})
        if not key:
            current_node.value = value
            current_node.update_hash()
            return

        first_char = key[0]
        current_node_is_new = False
        if first_char not in current_node.children:
            current_node_is_new = True
            current_node.children[first_char] = TrieNode()

        self._insert_node(current_node.children[first_char], key[1:], value, current_node_is_new)
        current_node.update_hash()

    def update_interaction(self, key: str, interaction: str):
        self.reset_update_history()
        key_hex = hexlify(key)
        self._update_interaction_node(self.root, key_hex, interaction)
        self.root.update_hash()
        self.update_history.reverse()
    
    def _update_interaction_node(self, current_node, key, interaction):
        self.update_history.append({
            "node": current_node, 
            "hash": current_node.hash, 
            "value": current_node.value, 
            "interaction": current_node.interaction, 
            "children": current_node.children,
            "new": False})
        
        if not key:
            current_node.interaction = interaction
            current_node.update_hash()
            return

        first_char = key[0]
        if first_char not in current_node.children:
            raise Exception("Cannot update interaction for key that does not exist")

        self._update_interaction_node(current_node.children[first_char], key[1:], interaction)
        current_node.update_hash()

    def rollback(self):
        for update in self.update_history:
            print('update', update["node"], update["hash"])
            if update["new"]:
                del update["node"]
            else:
                update["node"].hash = update["hash"]
                update["node"].value = update["value"]
                update["node"].interaction = update["interaction"]
                update["node"].children = update["children"]
        self.reset_update_history()


    def retrieve_value(self, key):
        key_hex = hexlify(key)
        return self._retrieve_node(self.root, key_hex)

    def _retrieve_node(self, current_node, key):
        if not key:
            return current_node.value

        first_char = key[0]
        if first_char in current_node.children:
            return self._retrieve_node(current_node.children[first_char], key[1:])
        else:
            return None
        
    def retrieve_interaction(self, key):
        key_hex = hexlify(key)
        return self._retrieve_interaction_node(self.root, key_hex)
    
    def _retrieve_interaction_node(self, current_node, key):
        if not key:
            return current_node.interaction

        first_char = key[0]
        if first_char in current_node.children:
            return self._retrieve_interaction_node(current_node.children[first_char], key[1:])
        else:
            return None
        
    
    def get_root_hash(self):
        return self.root.hash
    
    def get_all_keys(self):
        return self._get_keys_from_node(self.root, "")

    def _get_keys_from_node(self, current_node, current_path):
        keys = []
        if current_node.value is not None:
            keys.append(current_path)

        for char, node in current_node.children.items():
            keys.extend(self._get_keys_from_node(node, current_path + char))

        return keys
    
    def get_json_representation(self, interaction=False):
        return self._get_json_from_node(
            current_node=self.root, 
            current_path="", 
            interaction=interaction)

    def _get_json_from_node(self, 
            current_node, 
            current_path,
            interaction=False):
        
        if current_node.is_junction:
            # If it's a junction or a leaf, start a new sub-dictionary
            result = {}
            for char, node in current_node.children.items():
                sub_path = current_path + char
                result[sub_path] = self._get_json_from_node(node, "")
            
            if interaction and current_node.interaction is not None:
                # Add the interaction at this junction
                result[current_path] = current_node.interaction
            elif not interaction and current_node.value is not None:
                # Add the value at this junction
                result[current_path] = current_node.value
            else:
                pass
            
            return result
        else:
            # Continue building the path
            for char, node in current_node.children.items():
                return self._get_json_from_node(node, current_path + char)

    def insert_many(self, keysValuePairs):
        for key, value in keysValuePairs:
            self.insert(key, value)

    def update_many_interactions(self, keysInteractionPairs):
        for key, interaction in keysInteractionPairs:
            self.update_interaction(key, interaction)
    
    def persist(self, db, interaction=False):
        trie_representation = self.get_json_representation(interaction=interaction)
        ser_trie_representation = serialize(trie_representation)
        if interaction:
            db.put(
                ("interaction_" + lakathash(ser_trie_representation)).encode('utf-8'), 
                ser_trie_representation)
        else:
            db.put(
                lakathash(ser_trie_representation).encode('utf-8'), 
                ser_trie_representation)

        
    
    def get_hexlified(self, key: str) -> str:
        return hexlify(key)


# class MerkleTrieRevertible(MerkleTrie):
#     def __init__(self):
#         super().__init__()
#         self._root_history = []

#     def insert(self, key, value):
#         self._root_history.append({
#             "node": self.root,
#             "hash": self.root.hash,
#             "interaction": self.root.interaction


#         })
#         super().insert(key, value)
#         self._root_history.append(self.root.hash)

#     def revert(self):
#         if len(self._root_history) > 1:
#             self._root_history.pop()
#             self.root.hash = self._root_history[-1]
#         else:
#             raise Exception("Cannot revert further")

#     def get_root_history(self):
#         return self._root_history

#     def get_root_history_hashes(self):
#         return [hash for hash in self._root_history]

#     def get_root_history_hashes_hex(self):
#         return [hexlify(hash) for hash in self._root_history]

# # Example usage
# trie = MerkleTrie()
# trie.insert("key1", "value1")
# print("Root hash:", trie.root.hash)  # Outputs the hash of the root node
# trie.insert("key2", "value2")

# print("Value for 'key1':", trie.retrieve_value("key1"))  # Outputs: value1
# print("Value for 'key2':", trie.retrieve_value("key2"))  # Outputs: value2
# print("Root hash:", trie.root.hash)  # Outputs the hash of the root node


# # Update the interaction for a key
# trie.update_interaction("key1", "interaction1")
# print("Root hash:", trie.root.hash)  # Outputs the hash of the root node


# # Retrieve the interaction for a key
# print("Interaction for 'key1':", trie.retrieve_interaction("key1"))  # Outputs: interaction1
# all_keys = trie.get_all_keys()
# print("All keys:", all_keys)  # Outputs: ['key1', 'key2']

# # test rollback
# print("Root hash before insertion:", trie.root.hash)
# all_keys = trie.get_all_keys()
# print("All keys before insertion:", all_keys)

# trie.insert("kez2", "value3")

# print("Root hash after insertion:", trie.root.hash)
# all_keys = trie.get_all_keys()
# print("All keys after insertion:", all_keys)  # Outputs: ['key1', 'key2']

# trie.rollback()
# print("Root hash after rollback:", trie.root.hash)
# all_keys = trie.get_all_keys()
# print("All keys after rollback:", all_keys) 
