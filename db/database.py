import plyvel
from collections.abc import Mapping
from typing import List, Tuple
from typing_extensions import Literal
from db.db_interface import DB_BASE


class DB(DB_BASE):

    def __init__(self, name: str='lakat', create: bool=True):
        self.name = name 
        if create:
            self.db = self.create(name)

    def create(self, name:str) :
        return plyvel.DB('/tmp/{name}/'.format(name=name), create_if_missing=True)

    def put(self, key:bytes, value: bytes):
        self.db.put(key, value)

    def get(self, key:bytes) -> bytes :
        return self.db.get(key)

    def delete(self, key:bytes):
        self.db.delete(key)
    
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
        self.db.close()

# db = plyvel.DB('/tmp/{name}/'.format(name='lakat_test_1'), create_if_missing=True)

# db.put(b'key', b'value')

# val = db.get(b'key')

# print('val',val)

# bytes(string, 'utf-8')