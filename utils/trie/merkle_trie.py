import binascii
from utils.encode.hashing import parse_cid, make_lakat_cid_and_serialize_from_suffix, deserialize, hexlify, deserialize_from_key, serialize
from typing import List, Tuple
from config.encode_cfg import DEFAULT_CODEC


class MerkleTrie:

    def __init__(self, db, namespace: int, branch_suffix: bytes = bytes(0)):
        self.db = db
        self.cache = {}
        self.root = bytes(0)
        self.__namespace = namespace
        self.branch_suffix = branch_suffix
        self.staged_root = bytes(0)
        self.staged_cache = {}
        self.staged_db = []

    def set_root(self, root_id=bytes(0), codec=0x0):
        """ Set the root of the trie to an empty root. Only used at initialization."""
        if root_id == bytes(0):
            _, staged = self.stage_root(codec=codec, inplace=True)
            # commit the staged root (and sets the root)
            self.commit()
            db_entries = staged["db"]
            return db_entries
        else:
            # get root_id from db
            node, code, in_cache = self.retrieve_node_from_cache_or_db(cid=root_id, put_to_cache_if_not_already=True)
            if code!=200:
                raise Exception("Root node not found in db.")
            # set root
            self.root = root_id
            # create db_entries
            _, current_codec, _ = parse_cid(root_id)
            serialized = serialize(node.__dict__, codec=current_codec)
            db_entries = [(root_id, serialized)]
            return db_entries

    def stage_root(self, codec=0x0, inplace=True):
        """ Stages an empty root for the trie. Only used at initialization."""
        codec == (DEFAULT_CODEC if codec==0x0 else codec)
        node = dict(value=None, children={}, path=[])
        key, value = self.get_trie_key_value_from_node(node, codec=codec)
        staged = dict(db=[(key, value)], cache={key: node})
        if inplace:
            self.staged_root = key
            self.staged_cache = staged['cache']
            self.staged_db = staged['db']
        return key, staged

    def get_trie_key_value_from_node(self, node: any, codec: int) -> Tuple[bytes, bytes]:
        return make_lakat_cid_and_serialize_from_suffix(
                node, codec=codec, namespace=self.__namespace, suffix=self.branch_suffix)


    def put(self, key: bytes, value, codec: int = 0x0) -> List[Tuple[bytes, bytes]]:
        _, staged = self.stage(key=key, value=value, codec=codec, inplace=True)
        self.commit()
        return staged["db"]
    

    def commit(self, staged_root=bytes(0), staged_db=[], staged_cache=dict(), inplace=True, commit_to_db=True):
        """ Commits the staged changes to the trie. Optionally puts the staged changes into the database."""
        if inplace:
            if commit_to_db:
                for cid, serialized in self.staged_db:
                    self.db.put(cid, serialized)
            self.cache.update(self.staged_cache)
            self.root = self.staged_root
            self.staged_root = bytes(0)
            self.staged_cache = {}
            self.staged_db = []
        else:
            if commit_to_db:
                for cid, serialized in staged_db:
                    self.db.put(cid, serialized)
            self.cache.update(staged_cache)
            self.root = staged_root


 
    def stage(self, key: bytes, value, codec: int = 0x0, inplace=True) -> Tuple[bytes, dict]:
        # get codec from cid
        if codec == 0x0:
            _, current_codec, _ = parse_cid(key)
        else:
            current_codec = codec

        staged = dict(db=list(), cache=dict())
        hex_path = hexlify(key)
        staged_root, staged = self._stage_recursive(current_cid=self.root, path=hex_path, value=value, codec=current_codec, staged=staged)
        if inplace:
            self.staged_root = staged_root
            self.staged_cache = staged['cache']
            self.staged_db = staged['db']
        return staged_root, staged


    def _stage_recursive(self, current_cid:bytes, path: List[int], value, codec: int, staged: dict, depth: int = 0) -> Tuple[bytes, dict]:
        
        if depth == len(path):
            # End of Leaf
            node = dict(value=value, children={}, path=path)
            leaf_cid, leaf_serialized = self.get_trie_key_value_from_node(node, codec=codec)
            staged['db'].append((leaf_cid, leaf_serialized))
            staged['cache'][leaf_cid] = node
            return leaf_cid, staged

        # Get the current node
        if current_cid==bytes(0):
            # current node doesnt exist yet
            node = dict(value=None, children={}, path=path[:depth])
        if current_cid in self.cache:
            # current node is in cache
            node = self.cache[current_cid]
        else:
            # try to get from db
            serialized = self.db.get(current_cid)
            if serialized is None:
                # current node doesnt exist yet or cannot be retrieved from db
                node = dict(value=None, children={}, path=path[:depth])
            else:
                # current node is in db but not in cache
                node = deserialize_from_key(key=current_cid, value=serialized)
                # put current node in cache ( even though it will be overwritten later )
                self.cache[current_cid] = node
                # TODO: Maybe doesnt need to go into cache.

        # Get the next node
        char = path[depth]
        if char not in node["children"]:
            child_cid = bytes(0)
        else:
            child_cid = node["children"][char]

        # Recurse to the next level
        updated_child_cid, staged = self._stage_recursive(current_cid=child_cid, path=path, value=value, codec=codec, staged=staged, depth=depth + 1)

        # Update this node
        node["children"][char] = updated_child_cid
        updated_cid, updated_serialized = self.get_trie_key_value_from_node(node, codec=codec)
        staged['db'].append((updated_cid, updated_serialized))
        staged['cache'][updated_cid] = node
        return updated_cid, staged
    

    def get(self, key: bytes) -> Tuple[any, bool]:
        hex_path = hexlify(key)
        return self._get_recursive(current_cid=self.root, path=hex_path)

    def _get_recursive(self, current_cid: bytes, path: List[int], depth: int = 0) -> Tuple[any, bool]:
        if current_cid == bytes(0):
            return None, 400  # Node does not exist

        # Retrieve node from cache or database
        node, code, in_cache = self.retrieve_node_from_cache_or_db(cid=current_cid, put_to_cache_if_not_already=True)

        if code!=200:
            return None, code

        if depth == len(path):
            return node.get('value'), 200  # Return the value at the leaf

        char = path[depth]
        child_cid = node["children"].get(char)
        if child_cid is None:
            return None, 500  # Child node does not exist

        return self._get_recursive(current_cid=child_cid, path=path, depth=depth + 1)
    

    def retrieve_node_from_cache_or_db(self, cid: bytes, put_to_cache_if_not_already:bool=False) -> Tuple[any, bytes, bool, bool]:
        node_in_cache = False
        if cid in self.cache:
            node = self.cache[cid]
            node_in_cache = True
        else:
            serialized = self.db.get(cid)
            if serialized is None:
                return None, 300, False  # Node does not exist in db
            node = deserialize_from_key(key=cid, value=serialized)
            # otherwise set into cached storage
            if put_to_cache_if_not_already:
                self.cache[cid] = node
                node_in_cache = True
        return node, 200, node_in_cache
            

    def load_into_cache(self, current_cid: bytes, depth: int = 0, allow_overwrite: bool = False):
        if self.cache and depth == 0 and not allow_overwrite:
            raise Exception("Cache is not empty. Cannot load into cache. Set allow_overwrite=True to overwrite or append the cache.")
        
        if current_cid == bytes(0) or current_cid in self.cache:
            # If the node is empty or already in cache, stop the recursion
            return

        # Fetch and deserialize the node from the database
        serialized_node = self.db.get(current_cid)
        if serialized_node is None:
            return  # Node not found in the database

        node = deserialize_from_key(key=current_cid, value=serialized_node)

        # Add the node to the cache
        self.cache[current_cid] = node

        # Recursively load all children into the cache
        for child_cid in node['children'].values():
            self.load_into_cache(child_cid, depth=depth + 1, allow_overwrite=allow_overwrite)