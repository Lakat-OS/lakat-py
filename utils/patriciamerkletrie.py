import rlp
from typing import List, Union, Mapping, Optional, Tuple
from hashlib import sha3_256 as keccak
from db.database import DB

# Node types for type hints
BranchNode = List[Union[bytes, str]]
ExtensionNode = LeafNode = List[bytes]

# Placeholder for NULL nodes
NULL = b''

def to_nibbles(key: bytes) -> List[int]:
    return [b for byte in key for b in divmod(byte, 16)]

def get_first_nibble(byte_string):
    return byte_string[0] >> 4

def compact_encode(hexarray: List[int]) -> bytes:
    term = 1 if hexarray[-1] == 16 else 0   
    if term: 
        hexarray = hexarray[:-1]
    oddlen = len(hexarray) % 2
    flags = 2 * term + oddlen
    if oddlen:
        hexarray = [flags] + hexarray
    else:
        hexarray = [flags] + [0] + hexarray
    o = bytes(hexarray[i] * 16 + hexarray[i+1] for i in range(0,len(hexarray),2))
    return o


class Node:
    def __init__(self, content, parent: Optional[bytes or None]= None):
        self.content = content
        self.parent = parent
    
    def encode(self):
        return rlp.encode(self.content)
    
    @property
    def hash(self):
        encoded = self.encode()
        if len(encoded) < 32:
            return encoded
        return keccak(encoded).digest()
    

    @property
    def type(self):
        if self.content == NULL:
            return 'Null'
        elif isinstance(self.content, list):
            if len(self.content) == 17:
                return 'Branch'
            elif len(self.content) == 2:
                # first item is the path in hex
                if get_first_nibble(self.content[0]) <= 1 :
                    return 'Extension'
                if get_first_nibble(self.content[0]) <= 3 :
                    return 'Leaf'
                raise Exception('Invalid node')
            else:
                raise Exception('Invalid node')
        else:
            raise Exception('Invalid node')

    def set_parent(self, parent:bytes):
        self.parent = parent    
    
    def put(self, db):
        db.put(self.hash, self.encode())
    
    def get_content(self, db):
        return db.get(self.hash)
    
    def get_value_entry(self):
        type = self.type
        if type == 'Leaf':
            return self.content[1]
        elif type == 'Branch':
            return self.content[16]
        else:
            raise Exception('Invalid node')
        
    def update_content(self, content):
        self.content = content

    def remove_from_db(self, db):
        db.delete(self.hash)

    def __eq__(self, other):
        return self.hash() == other.hash()


class MerklePatriciaTrie:

    def __init__(self, db: DB, root: Optional[bytes] = NULL):
        self.root = root
        self.db = db
        self.nodes : Mapping[bytes, Node] = {}
        if root:
            self.nodes = {root: Node(self._decode_node(root))}

    def get(self, key: str) -> str:
        key = self._to_nibbles(bytes.fromhex(key[2:]))
        return self._get(self.root, key)

    def insert(self, key: str, value: bytes):
        # update also the hashes and the root along the path
        key = self._to_nibbles(bytes.fromhex(key[2:]))
        path = self._insert(self.root, key, value, [])
        self.update_nodes(path)


    def _get(self, node_hash: bytes, path: List[int], parent:Optional[bytes or None]=None) -> bytes:
        if not node_hash:
            raise Exception('Invalid node')
        
        node = self._get_node(node_hash, parent=parent)
        node_type = node.type
        if node_type == 'Leaf':
            return node.content[1]
        elif node_type == 'Branch':
            if len(path)!=0:
                return self._get(node.content[path[0]], path[1:], parent=node_hash)
            else:
                return node.content[16]
        elif node_type == 'Extension':
            prefix = node.content[0]
            if prefix == path[:len(prefix)]:
                return self._get(node.content[1], path[len(prefix):], parent=node_hash)
            else:
                raise Exception('Invalid node')
        else:
            raise Exception('Invalid node')
        

    def _get_node(self, node_hash: bytes, parent: Optional[bytes or None] = None) -> Node:
        node = self.nodes.get(node_hash)
        if node is None:
            # get the node data from the db and create a node instance
            content = self._decode_node(node_hash)
            node = Node(content=content, parent=parent)
            self.nodes.update({node_hash: node})
        return node


    def _insert(self, node_hash: bytes, key: List[int], value: bytes, path=List[Tuple[bytes,str]]) -> List[bytes]:
        node : Node
        if len(path)==0:
            node = self._get_node(node_hash)
        else:
            node = self._get_node(node_hash, parent=path[-1])
        
        node_type = node.type

        path.append((node_hash, node_type))

        if node_type == 'Null':
            # new_node = self.newNode([key, value])
            print('Whaatt this shouldnt happen')
            return path

        if node_type == 'Leaf':
            # TODO: actually the key must first be derived from the path
            old_key = node.content[0]

            if old_key == key:
                # updates the node, but not the database
                content = node.content
                content[1] = value
                node.update(content)
                return path
            else:
                # There are two cases. Either the keys have a common prefix or not
                common_prefix, old_key_rest, new_key_rest = self._common_prefix(old_key, key)
                if common_prefix:
                    # create a new extension node
                    new_extension = [common_prefix, NULL]

                    # node needs to be updated in the first argument
                    node_content = node.content
                    node_content[0] = old_key_rest #TODO: again, the content is created from the key
                    
                    # old parent 
                    old_parent = node.parent

                    # drop the previous db entry
                    node.remove_from_db(self.db)

                    # update the content of the node
                    node.update_content(node_content)

                    # first drop the node from the dictionary
                    self.nodes.pop(node.hash)
                    # then add the new one
                    node.put(self.db)
                    # then update the nodes dictionary
                    self.nodes.update({node.hash: node})
                    # no need to update the parent, because that will be done later in the backpropagation function

                    # create new node 
                    new_leaf = Node([new_key_rest, value]) # TODO: again, the content is created from the key

                    # create new branch content
                    branch_content = [NULL]*17
                    branch_content[old_key_rest[0]] = node.hash
                    branch_content[new_key_rest[0]] = new_leaf.hash

                    # create new branch node
                    branch_node = Node(branch_content)
                    new_extension[1] = branch_node.hash

                    # create extension node
                    extension_node = Node(new_extension, parent=old_parent)
                    branch_node.set_parent(extension_node.hash)
                    new_leaf.set_parent(branch_node.hash)
                    node.set_parent(branch_node.hash)

                    # update the nodes dictionary
                    self.nodes.update({
                        new_leaf.hash: new_leaf,
                        branch_node.hash: branch_node,
                        extension_node.hash: extension_node})
                    
                    # update the path
                    # first remove the old leaf
                    path.pop()
                    # then extend with the extension node, then the branching node and then the new leaf
                    path.extend(
                        [
                            (extension_node.hash, 'Extension'),
                            (branch_node.hash, 'Branch'),
                            (new_leaf.hash, 'Leaf')
                        ])
                    
                    return path


                if not common_prefix:
                    
                    # create a new leaf node
                    new_leaf = Node([key, value])

                    # create a new branch node
                    branch_node = Node([NULL]*17)
                    
                    # update the parent of the leaf node
                    new_leaf.set_parent(branch_node.hash)
                    # update the parent of the old node
                    node.set_parent(branch_node.hash)
                    # update the content of the branch node
                    branch_node.content[key[0]] = new_leaf.hash
                    branch_node.content[old_key[0]] = node.hash

                    # update the nodes dictionary
                    self.nodes.update({
                        new_leaf.hash: new_leaf,
                        branch_node.hash: branch_node
                    })

                    # update the path
                    # first remove the old leaf
                    path.pop()
                    # then extend with the branching node and then the new leaf
                    path.extend(
                        [
                            (branch_node.hash, 'Branch'),
                            (new_leaf.hash, 'Leaf')
                        ])
                    
                    return path

                # turning the leaf not into a branch 
                # Adding the new leaf to the branch
                new_leaf = Node([key, value])
                new_content = [NULL]*16 + [node.content[1]]
                new_content[key[0]] = new_leaf.hash
                node.update_content(new_content)
                new_leaf.set_parent(node.hash)
                path.append((new_leaf.hash, 'Leaf'))
                self.nodes.update({new_leaf.hash: new_leaf})
                return path

        if node_type == 'Branch':
            if len(key) == 0:
                content = node.content
                content[-1]= value
                node.update_content(content)
                return path
            else:
                sub_node_hash = node.content[key[0]]
                return self._insert(sub_node_hash, key[1:], value, path)

        if node_type == 'Extension':
            common_prefix = [i for i, j in zip(node.content[0], key) if i == j]
            if len(common_prefix) != len(node.content[0]):
                # Need to split the extension node
                old_extension = node.content[0][len(common_prefix):]
                new_extension = key[len(common_prefix):]
                branch_node = self.newNode(['']*17)
                if old_extension:
                    old_node = self.newNode([old_extension, node.content[1]])
                    branch_node.content[old_extension[0]] = old_node.hash
                else:
                    branch_node.content[-1] = node.content[1]
                if new_extension:
                    new_node = self.newNode([new_extension, value])
                    branch_node.content[new_extension[0]] = new_node.hash
                else:
                    branch_node.content[-1] = value
                return path
            else:
                # Continue down the path
                sub_node_hash = node.content[1]
                sub_path = self._insert(sub_node_hash, key[len(common_prefix):], value, path)
                return sub_path
        return path  # Return the path if nothing matched, though this should never happen



    def _insert(self, node_hash: bytes, key: List[int], value: bytes, path=List[bytes]) -> List[bytes]:
        if not key:
            return value
        node : Node = self._decode_node(node_hash)

        if isinstance(node, LeafNode) or isinstance(node, ExtensionNode):
            prefix, _ = node
            common_prefix = self._common_prefix(prefix, key)
            if not common_prefix:
                new_node = [NULL] * 17
                new_node[key[0]] = self._insert(NULL, key[1:], value)
                new_node[prefix[0]] = self._insert(NULL, prefix[1:], node[1])
            elif len(common_prefix) == len(prefix):
                node[1] = self._insert(node[1], key[len(common_prefix):], value)
                new_node = node
            else:
                new_node = [common_prefix, NULL]
                new_node[1] = self._insert(NULL, key[len(common_prefix):], value)
            return self._encode_node(new_node)
        elif isinstance(node, BranchNode):
            node[key[0]] = self._insert(node[key[0]], key[1:], value)
            return self._encode_node(node)

    def _decode_node(self, node_hash: bytes):
        node = self.db.get(node_hash) 
        if node:
            return rlp.decode(node)
        else:
            raise Exception('Invalid node')


    def prune_nodes_cache(self):
        if self.nodes:
            self.nodes = {self.root: self.nodes[self.root]}


    def _encode_node(self, node: Union[LeafNode, ExtensionNode, BranchNode]) -> bytes:
        encoded_node = rlp.encode(node)
        if len(encoded_node) < 32:
            return encoded_node
        node_hash = keccak(encoded_node).digest()
        db.put(node_hash, encoded_node)
        return node_hash

    @staticmethod
    def _to_nibbles(key: bytes) -> List[int]:
        return [b for byte in key for b in divmod(byte, 16)]

    @staticmethod
    def _common_prefix(a: List[int], b: List[int]) -> List[int]:
        common = []
        a_surplus = []
        b_surplus = []
        common_flag = True
        for x, y in zip(a, b):
            if x == y and common_flag:
                common.append(x)
            else:
                common_flag = False
                a_surplus.append(x)
                b_surplus.append(y)
        return common, a_surplus, b_surplus
