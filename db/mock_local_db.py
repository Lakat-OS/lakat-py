## create a file storage mock db

import os
import time
import json
import shutil
import multicodec
import multihash
from typing import List, Tuple
from typing_extensions import Literal
from collections.abc import Mapping
from db.db_interfaces import DB_BASE
from config.db_cfg import (
    DEV_TRIE_SUFFIX, 
    TRIE_TYPE, 
    INTERACTION_TRIE_FOLDER,
    NAME_TRIE_FOLDER,
    DATA_TRIE_FOLDER,
    HASH_ENCODING_STYLE,
    TRIE_INTERACTION_DUMP_TYPE,
    NUMBER_OF_SUFFIXLESS_NAMESPACES)

from db.namespaces import (
    BRANCH_NS,
    NAME_RESOLUTION_TRIE_NS,
    INTERACTION_TRIE_NS,
    DATA_TRIE_NS,
    SUBMIT_NS,
    SUBMIT_TRACE_NS)

from utils.encode.hashing import deserialize, parse_lakat_cid, get_namespace_from_lakat_cid
from utils.encode.language import decode_bytes
from utils.encode.bytes import key_encoder, key_decoder
from utils.encode.json import jsondump

trie_folders = {
    NAME_RESOLUTION_TRIE_NS: NAME_TRIE_FOLDER,
    INTERACTION_TRIE_NS: INTERACTION_TRIE_FOLDER,
    DATA_TRIE_NS: DATA_TRIE_FOLDER
}

class MOCK_DB(DB_BASE):

    def __init__(self, path: str, name: str='lakat', crop_filename_after=10):
        self.name = name 
        self.__path = path
        self.__crop_filename_after = crop_filename_after
        self.db : str = self.__create(name, and_assign_to_db=False)
        self.staged = dict()
        self.staged_indices = list()
    
    def __create(self, name:str, and_assign_to_db=True) :
        path = os.path.join(self.__path, name)
        if not os.path.exists(path):
            os.makedirs(path)
        name_trie_path = os.path.join(path, NAME_TRIE_FOLDER)
        data_trie_path = os.path.join(path, DATA_TRIE_FOLDER)
        interaction_trie_path = os.path.join(path, INTERACTION_TRIE_FOLDER)

        if not os.path.exists(name_trie_path):
            os.makedirs(name_trie_path)
        if not os.path.exists(data_trie_path):
            os.makedirs(data_trie_path)
        if not os.path.exists(interaction_trie_path):
            os.makedirs(interaction_trie_path)

        # create an index json file:
        with open(os.path.join(path, "index.json"), "w") as f:
            jsondump([], f)
        if and_assign_to_db:
            self.db = path
        return path
    

    def get_filename(self, filename: str):
        if self.__crop_filename_after == 0:
            return filename
        else:
            return filename[:self.__crop_filename_after]
    

    def stage(self, key:bytes, value: bytes):
        staged, staged_indices = self._create_new_db_entries(key, value)
        self.staged.update(staged)
        self.staged_indices.extend(staged_indices)

    
    def stage_many(self, entries: List[Tuple[bytes, bytes]]):
        for key, value in entries:
            self.stage(key, value)
        

    def commit(self):
        ## first commit all the self.staged entries 
        self._push_staged(self.staged, self.staged_indices)
        ## reset the staged entries
        self.staged = dict()
        self.staged_indices = list()


    def put(self, key:bytes, value: bytes):
        staged, staged_indices = self._create_new_db_entries(key, value)
        self._push_staged(staged, staged_indices)

    
    def get(self, key:bytes) -> bytes :
        namespace = get_namespace_from_lakat_cid(key)

        encoded_key = key_encoder(key)

        is_trie_data = False
        for ns, folder in trie_folders.items():
            if namespace == ns:
                file_path = os.path.join(self.db, folder, self.get_filename(encoded_key) + ".json")
                is_trie_data = True
                break
        if not is_trie_data:
            file_path = os.path.join(self.db, self.get_filename(encoded_key) + ".json")
            
        # check whether file exists
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            return key_decoder(data['serialized'])
        

    def get_new_index_entry(self, request_type, namespace, alg_id, codec_id, digest, core, peri, file_path, key):
        return {
            'request-type': request_type,
            'namespace': namespace,
            'codec': multicodec.constants.CODE_TABLE[codec_id],
            'hash-algorithm': multihash.constants.CODE_HASHES[alg_id],
            'digest': digest,
            'core': core,
            'peri': peri,
            'timestamp': time.time(),
            'filepath': file_path,
            'key': key}


    
    def _create_new_db_entries(self, key:bytes, value: bytes):
        encoded_key = key_encoder(key)
        
        file_path = os.path.join(self.db, self.get_filename(encoded_key)+ ".json")
        
        # get all information from the key
        (version, 
         codec_id, 
         alg_id, 
         digest_length, 
         digest, 
         namespace, 
         suffix_length_length, 
         crop,
         branch_id, 
         parent_branch_id) = parse_lakat_cid(key)

        if namespace == BRANCH_NS:
            data = {
                'info': {
                    "key-raw": repr(key), 
                    "key-encoded": encoded_key, 
                    "value-raw": repr(value), 
                    "value-encoded": key_encoder(value)},
                'serialized': key_encoder(value)}
        else:
            deserialized = deserialize(value, codec=codec_id)
            if namespace == SUBMIT_NS:
                deserialized["submit_msg"] = decode_bytes(deserialized["submit_msg"])
            if namespace == SUBMIT_TRACE_NS:
                nR = [[decode_bytes(entry[0]), entry[1]] for entry in deserialized["nameResolution"] ]
                deserialized["nameResolution"] = nR
        
            data = {'unserialized': deserialized, 'serialized': key_encoder(value)}

        is_trie_data = False
        for ns, folder in trie_folders.items():
            if namespace == ns:
                file_path = os.path.join(self.db, folder, self.get_filename(encoded_key) + ".json")
                is_trie_data = True
                break
        if not is_trie_data:
            file_path = os.path.join(self.db, self.get_filename(encoded_key) + ".json")

        request_type = 'update' if os.path.exists(file_path) else 'put'

        staged = {file_path: data}
        staged_indices = list()

        if not namespace in trie_folders:
            if suffix_length_length == 0:
                peri = ""
                core = ""
            else:
                peri = key_encoder(branch_id)
                core = key_encoder(parent_branch_id)

            new_index_entry = self.get_new_index_entry(request_type=request_type, namespace=namespace, alg_id=alg_id, codec_id=codec_id, digest=key_encoder(digest), core=core, peri=peri, file_path=file_path, key=repr(key))
            
            staged_indices.append(new_index_entry)
        
        return staged, staged_indices
    

    def _push_staged(self, staged, staged_indices):
        ## first commit all the self.staged entries 
        for file_path, data in staged.items():
            with open(file_path, 'w') as file:
                jsondump(data, file)
        ## then commit all the index entries
        with open(os.path.join(self.db, "index.json"), "r") as f:
            index = json.load(f)
            index.extend(staged_indices)
        with open(os.path.join(self.db, "index.json"), "w") as f:
            jsondump(index, f)


    def multiquery(self, queries: List[Tuple[Literal["put", "get", "delete"], List[bytes]]]) -> List[Tuple[Literal["put", "get", "delete"], bool or bytes]]:
        results = list()
        for queryType, arguments in queries:
            if queryType == "put":
                self.put(arguments[0], arguments[1])
                results.append((queryType, True))
            elif queryType == "get":
                results.append((queryType, self.get(arguments[0])))
            elif queryType == "delete":
                self.delete(arguments[0])
                results.append((queryType, True))
            else:
                raise Exception("Invalid query type")
        return results


    def close(self):
        # delete the directory and all its files
        shutil.rmtree(self.db)

    def restart(self, name=None):
        self.close()
        if name:
            self.__create(name)
            return name
        else:
            self.__create(self.name)
            return self.name


class PRIMITIVE_MOCK_DB:
    def __init__(self):
        self.key_values = {}

    def put(self, key, value):
        self.key_values[key] = value

    def get(self, key):
        return self.key_values.get(key)
    
