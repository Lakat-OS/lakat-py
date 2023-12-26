## create a file storage mock db

import os
import time
import json
import shutil
from typing import List, Tuple
from typing_extensions import Literal
from collections.abc import Mapping
from db.db_interfaces import DB_BASE
from config.db_cfg import (
    DEV_TRIE_SUFFIX, 
    TRIE_TYPE, 
    INTERACTION_TRIE_FOLDER,
    TRIE_FOLDER,
    TRIE_INTERACTION_DUMP_TYPE)

from utils.serialize.codec import serialize, unserialize
from utils.encode.check_if_hex import are_keys_hexadecimal


class MOCK_DB(DB_BASE):

    def __init__(self, path: str, name: str='lakat', crop_filename_after=10, create: bool=True):
        self.name = name 
        self.__path = path
        self.__crop_filename_after = crop_filename_after
        self.db: str = ""
        if create:
            self.db = self.create(name, and_assign_to_db=False)
    
    def create(self, name:str, and_assign_to_db=True) :
        path = os.path.join(self.__path, name)
        if not os.path.exists(path):
            os.makedirs(path)
        trie_path = os.path.join(path, TRIE_FOLDER)
        interaction_trie_path = os.path.join(path, INTERACTION_TRIE_FOLDER)
        if not os.path.exists(trie_path):
            os.makedirs(trie_path)
        if not os.path.exists(interaction_trie_path):
            os.makedirs(interaction_trie_path)

        # create an index json file:
        with open(os.path.join(path, "index.json"), "w") as f:
            json.dump([], f)
        if and_assign_to_db:
            self.db = path
        return path

    def put(self, key:bytes, value: bytes):

        
        file_path = os.path.join(self.db, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        request_type = 'update' if os.path.exists(file_path) else 'put'
        # assign object type
        object_type = 'bucket'
        unserialized = unserialize(value)
        if are_keys_hexadecimal(unserialized):
            object_type = "trie_dump"
        elif "schema_id" in unserialized:
            object_type = "bucket_" + str(unserialized["schema_id"])
        elif "parent_submit_id" in unserialized:
            object_type = "submit"
        elif "parentBranch" in unserialized:
            object_type = "branch"
        elif "changesTrace" in unserialized:
            object_type = "trace"
        else:
            object_type = "other"

        for k in ["data", "refs"]:
            if k in unserialized:
                unserialized[k] = unserialize(unserialized[k])
        if "public_key" in unserialized:
            unserialized["public_key"] = unserialized["public_key"].decode('utf-8')
        # check if its a trie node
        

        data = {}
        if are_keys_hexadecimal(unserialized):
            data.update(unserialized)
        else:
            data.update({'unserialized': unserialized, 'serialized': value})

        if entry_type == TRIE_TYPE:
            file_path = os.path.join(self.db, TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        elif entry_type == TRIE_INTERACTION_DUMP_TYPE:
            file_path = os.path.join(self.db, INTERACTION_TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        else:
            pass

        with open(file_path, 'w') as file:
            jsondump(data, file)

        if entry_type != TRIE_TYPE:
            self.update_index(request_type, object_type, file_path, key.decode('utf-8'))

    
    def get(self, key:bytes, entry_type: str = "db") -> bytes :
        
        
        if entry_type == TRIE_TYPE:
            file_path = os.path.join(self.db, TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")

        elif entry_type == TRIE_INTERACTION_DUMP_TYPE:
            file_path = os.path.join(self.db, INTERACTION_TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
            
        else:
            file_path = os.path.join(self.db, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        
        # check whether file exists
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as file:
            data = jsonload(file)
            return data['serialized']
        
    
    def update_index(self, request_type, object_type, file_path, key):
        with open(os.path.join(self.db, "index.json"), "r") as f:
            index = jsonload(f)

            index.append({
                'request-type': request_type,
                'object-type': object_type,
                'timestamp': time.time(),
                'filepath': file_path,
                'key': key
            })
        with open(os.path.join(self.db, "index.json"), "w") as f:
            jsondump(index, f)

    def delete(self, key:bytes, entry_type: str="db"):
        if entry_type == TRIE_TYPE:
            file_path = os.path.join(self.db, TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        elif entry_type == TRIE_INTERACTION_DUMP_TYPE:
            file_path = os.path.join(self.db, INTERACTION_TRIE_FOLDER, key[:self.__crop_filename_after].decode('utf-8') + ".json")
        else:
            file_path = os.path.join(self.db, key[:self.__crop_filename_after].decode('utf-8') + ".json")


        # remove the file
        os.remove(file_path)

        if entry_type != TRIE_TYPE:
            request_type = 'delete'
            object_type = 'unknown'
            self.update_index(request_type, object_type, file_path, key.decode('utf-8'))


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
