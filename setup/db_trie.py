from utils.trie.trie import MerkleTrie
from db.database import DB
from db.mockdb import MOCK_DB
from config.db_cfg import DB_NAME, DB_FOLDER
import os


# db = DB(name=DB_NAME)
db_path = os.path.abspath(os.path.join(os.getcwd(), DB_FOLDER))
db = MOCK_DB(path=db_path, name=DB_NAME, create=True)
# TODO: SHOULD be created only on branch creation
trie = MerkleTrie(db=db, branchId="")

