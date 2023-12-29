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
    TRIE_INTERACTION_DUMP_TYPE)

from db.namespaces import (
    NAME_RESOLUTION_TRIE_NS,
    INTERACTION_TRIE_NS,
    DATA_TRIE_NS)

from utils.encode.hashing import deserialize, parse_lakat_cid, get_namespace_from_lakat_cid
from utils.encode.language import decode_bytes
from utils.encode.bytes import key_encoder
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
    


    def put(self, key:bytes, value: bytes):

        encoded_key = key_encoder(key)
        
        file_path = os.path.join(self.db, self.get_filename(encoded_key)+ ".json")

        request_type = 'update' if os.path.exists(file_path) else 'put'
        
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

        deserialized = deserialize(value, codec=codec_id)

        if "msg" in deserialized:
            deserialized["msg"] = decode_bytes(deserialized["msg"])
        
        data = {'unserialized': deserialized, 'serialized': key_encoder(value)}

        is_trie_data = False
        for ns, folder in trie_folders.items():
            if namespace == ns:
                file_path = os.path.join(self.db, folder, self.get_filename(encoded_key) + ".json")
                is_trie_data = True
                print('is trie data of namespace ', ns)
                # print encoded key and encoded cropped key
                print('encoded key: ', encoded_key)
                print('encoded cropped key: ', self.get_filename(encoded_key))
                break
        if not is_trie_data:
            file_path = os.path.join(self.db, self.get_filename(encoded_key) + ".json")

        with open(file_path, 'w') as file:
            jsondump(data, file)

        if not namespace in trie_folders:
            if suffix_length_length == 0:
                peri = ""
                core = ""
            else:
                peri = key_encoder(branch_id)
                core = key_encoder(parent_branch_id)

            self.update_index(request_type=request_type, namespace=namespace, alg_id=alg_id, 
                codec_id=codec_id, digest=key_encoder(digest), core=core, peri=peri, file_path=file_path, key=repr(key))

    
    def get(self, key:bytes) -> bytes :
        print('we are requestions key: ', key)
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
            return data['serialized']
        
    
    def update_index(self, request_type, namespace, alg_id, codec_id, digest, core, peri, file_path, key):
        with open(os.path.join(self.db, "index.json"), "r") as f:
            index = json.load(f)

            index.append({
                'request-type': request_type,
                'namespace': namespace,
                'codec': multicodec.constants.CODE_TABLE[codec_id],
                'hash-algorithm': multihash.constants.CODE_HASHES[alg_id],
                'digest': digest,
                'core': core,
                'peri': peri,
                'timestamp': time.time(),
                'filepath': file_path,
                'key': key
            })

        with open(os.path.join(self.db, "index.json"), "w") as f:
            jsondump(index, f)

    # def delete(self, key:bytes, entry_type: str="db"):
    #     if entry_type == TRIE_TYPE:
    #         file_path = os.path.join(self.db, TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
    #     elif entry_type == TRIE_INTERACTION_DUMP_TYPE:
    #         file_path = os.path.join(self.db, INTERACTION_TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
    #     else:
    #         file_path = os.path.join(self.db, key[:self.__crop_filename_after].decode('utf-8') + ".json")


    #     # remove the file
    #     os.remove(file_path)

    #     if entry_type != TRIE_TYPE:
    #         request_type = 'delete'
    #         object_type = 'unknown'
    #         self.update_index(request_type, object_type, file_path, key.decode('utf-8'))


#     def multiquery(self, queries: List[Tuple[Literal["put", "get", "delete"], List[bytes]]]) -> List[Tuple[Literal["put", "get", "delete"], bool or bytes]]:
#         results = list()
#         for queryType, arguments in queries:
#             if queryType == "put":
#                 self.put(arguments[0], arguments[1])
#                 results.append((queryType, True))
#             elif queryType == "get":
#                 results.append((queryType, self.get(arguments[0])))
#             elif queryType == "delete":
#                 self.delete(arguments[0])
#                 results.append((queryType, True))
#             else:
#                 raise Exception("Invalid query type")
#         return results


#     def close(self):
#         # delete the directory and all its files
#         shutil.rmtree(self.db)


class PRIMITIVE_MOCK_DB:
    def __init__(self):
        self.key_values = {}

    def put(self, key, value):
        self.key_values[key] = value

    def get(self, key):
        return self.key_values.get(key)
    