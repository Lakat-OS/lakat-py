import plyvel
from collections.abc import Mapping
from typing import List, Tuple
from typing_extensions import Literal
from db.db_interfaces import DB_BASE

# from config.db_cfg import DEV_DB_PATH
class DB(DB_BASE):
    def __init__(self, name: str = 'lakat', create: bool = True):
        self.name = name
        self.staged = {}  # Dictionary to hold staged changes
        if create:
            self.db = self.create(name)

    def create(self, name: str):
        return plyvel.DB(f'/tmp/{name}/', create_if_missing=True)

    def put(self, key: bytes, value: bytes):
        self.db.put(key, value)

    def get(self, key: bytes) -> bytes or None:
        if not key:
            return None
        value = self.db.get(key)
        return value if value else b''

    def delete(self, key: bytes):
        self.db.delete(key)

    # Staging function
    def stage(self, key: bytes, value: bytes):
        self.staged[key] = value

    def stage_many(self, entries: List[Tuple[bytes, bytes]]):
        for key, value in entries:
            self.stage(key, value)

    # Commit function
    def commit(self):
        for key, value in self.staged.items():
            self.put(key, value)
        self.staged.clear()

    # Restart function
    def restart(self, name: str = None):
        self.close()
        self.db = self.create(name or self.name)
    
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