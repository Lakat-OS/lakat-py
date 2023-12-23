from typing import List, Tuple, Literal

class DB_BASE:

    def create(self, name:str):
        pass

    def put(self, key:bytes, value: bytes):
        pass

    def get(self, key:bytes) -> bytes :
        pass

    def delete(self, key:bytes):
        pass
    
    def multiquery(self, queries: List[Tuple[Literal["put", "get", "delete"], List[bytes]]]) -> List[Tuple[Literal["put", "get", "delete"], bool or bytes]]:
        pass

    def close(self):
        pass


class DHT:

    def store(self, key: str, value: str):
        pass

    def retrieve(self, key: str) -> str:
        pass