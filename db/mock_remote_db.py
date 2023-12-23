from db.db_interfaces import DHT
from db.local_db import DB_BASE
from db.mock_local_db import MOCK_DB

class MOCK_REMOTE_DB(DHT):

    def __init__(self, db: MOCK_DB):
        self.db = db

    def store(self, key: str, value: str):
        self.db.put(key, value)

    def retrieve(self, key: str) -> str:
        self.db.get(key)
