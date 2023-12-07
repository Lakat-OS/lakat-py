from lakat.trie import MerkleTrie
from db.database import DB
from db.mockdb import MOCK_DB
from config.db_cfg import DB_NAME
import os

trie = MerkleTrie()
# db = DB(name=DB_NAME)
db_path = os.path.abspath(os.path.join(os.getcwd(), "mockdb"))
db = MOCK_DB(path=db_path, name=DB_NAME, create=True)

