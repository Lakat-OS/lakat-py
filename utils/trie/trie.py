import binascii
from utils.encode.hashing import lakathash
from utils.serialize.codec import serialize, unserialize
from config.db_cfg import TRIE_INTERACTION_DUMP_TYPE, TRIE_TYPE
from utils.trie.node import TrieNode


def hexlify(data: str) -> str:
    return binascii.hexlify(data.encode('utf-8')).decode('utf-8')

# def hash_data(data):
#     return hashlib.sha256(data.encode('utf-8')).hexdigest()

class MerkleTrie:
    def __init__(self, db, branchId):
        self.root = TrieNode('')
        self.update_history = []
        self.db = db
        self.branchId = branchId

    def reset_update_history(self):
        self.update_history = []

    def insert(self, key: str, value, from_cache=False):
        if from_cache:
            _insert(self, key=key, value=value)
        else:
            # TODO: insert just through db calls
            pass



    def _insert(self, key: str, value):
        self.reset_update_history()
        # reverse the hexlified key
        rev_key_hex = list(reversed(hexlify(key)))
        self._insert_node(self.root, rev_key_hex, self.root.path, value, False)
        self.root.update_hash(self.db)
        self.update_history.reverse()

    def _insert_node(self, current_node: TrieNode, rev_key, path, value, current_node_is_new=False):
        self.update_history.append({
            "node": current_node, 
            "hash": current_node.hash, 
            "value": current_node.value, 
            "interaction": current_node.interaction, 
            "children": current_node.children,
            "new": current_node_is_new})
        if not rev_key:
            current_node.value = value
            current_node.update_hash(self.db)
            return

        first_char = rev_key.pop()
        path += first_char
        current_node_is_new = False
        if first_char not in current_node.children:
            current_node_is_new = True
            current_node.children[first_char] = TrieNode(path)

        self._insert_node(current_node.children[first_char], rev_key, path, value, current_node_is_new)
        current_node.update_hash(self.db)


    def update_interaction(self, key: str, interaction: str):
        self.reset_update_history()
        rev_key_hex = list(reversed(hexlify(key)))
        self._update_interaction_node(self.root, rev_key_hex, self.root.path, interaction)
        self.root.update_hash(self.db)
        self.update_history.reverse()
    
    def _update_interaction_node(self, current_node, rev_key, path, interaction):
        self.update_history.append({
            "node": current_node, 
            "hash": current_node.hash, 
            "value": current_node.value, 
            "interaction": current_node.interaction, 
            "children": current_node.children,
            "new": False})
        
        if not rev_key:
            current_node.interaction = interaction
            current_node.update_hash(self.db)
            return

        first_char = rev_key.pop()
        # path += first_char
        if first_char not in current_node.children:
            raise Exception("Cannot update interaction for key that does not exist")

        self._update_interaction_node(current_node.children[first_char], rev_key, interaction)
        current_node.update_hash(self.db)

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
    
    def persist(self, interaction=False):
        trie_representation = self.get_json_representation(interaction=interaction)
        ser_trie_representation = serialize(trie_representation)
        if interaction:
            self.db.put(
                lakathash(ser_trie_representation).encode('utf-8'), 
                ser_trie_representation, TRIE_INTERACTION_DUMP_TYPE)
        else:
            self.db.put(
                lakathash(ser_trie_representation).encode('utf-8'), 
                ser_trie_representation)

    def load_trie_from_db(self, root_hash):
        if not self.root.is_leaf:
            raise Exception("Current Trie must be empty to load from database")
        self._load_trie_node_from_db(self.root, root_hash)


    def _load_trie_node_from_db(self, current_node, hash):
        # fetch the serialized data from the database
        serialized = self.db.get(hash.encode('utf-8'), entry_type=TRIE_TYPE)
        if serialized is None:
            raise Exception("Root hash not found in database")
        data = unserialize(serialized)
        children_ids = data["children"]
        # update the node with the data except for the children
        current_node.value = data["value"]
        current_node.path = data["path"]
        current_node.hash = hash
        current_node.interaction = data["interaction"]
        # load the children
        current_node.children = {k: TrieNode() for k in children_ids.keys()}
        for char, child_hash in children_ids.items():
            self._load_trie_node_from_db(current_node.children[char], child_hash)
            # verify that the hash of the child is correct
            calculated_hash = current_node.children[char].get_hash()
            if current_node.children[char].hash != calculated_hash:
                raise Exception(f"Hash of child {char} of node {current_node.path} is incorrect")

    
    def get_hexlified(self, key: str) -> str:
        return hexlify(key)
    
